"""Conexão com o Firebase: Admin SDK + Cloud Firestore.

Este é o ÚNICO módulo que lê as credenciais. Nunca cai para outro banco em silêncio.
"""
from __future__ import annotations

import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore

REQUIRED_KEYS = ("type", "project_id", "private_key", "client_email")


class FirebaseConfigError(RuntimeError):
    """Credenciais ausentes ou inválidas (mensagem segura para exibir ao usuário)."""


def _load_config() -> dict:
    try:
        raw = st.secrets["firebase"]
    except Exception as exc:  # secrets.toml ausente ou sem a seção [firebase]
        raise FirebaseConfigError(
            "Credenciais do Firebase não encontradas. Crie o arquivo "
            ".streamlit/secrets.toml com a seção [firebase] (veja secrets.toml.example)."
        ) from exc
    config = dict(raw)
    missing = [key for key in REQUIRED_KEYS if not config.get(key)]
    if missing:
        raise FirebaseConfigError(f"Campos ausentes na seção [firebase]: {', '.join(missing)}.")
    config["private_key"] = str(config["private_key"]).replace("\\n", "\n")
    if "BEGIN PRIVATE KEY" not in config["private_key"]:
        raise FirebaseConfigError(
            "A chave privada parece malformada. Copie o campo private_key do JSON "
            "da conta de serviço sem alterá-lo."
        )
    return config


def init_app():
    """Inicializa o Admin SDK uma única vez (seguro contra reruns do Streamlit)."""
    if firebase_admin._apps:
        return firebase_admin.get_app()
    config = _load_config()
    try:
        return firebase_admin.initialize_app(credentials.Certificate(config))
    except ValueError as exc:
        raise FirebaseConfigError(
            "Credenciais do Firebase inválidas. Gere uma nova chave da conta de serviço."
        ) from exc


@st.cache_resource(show_spinner=False)
def get_db():
    """Cliente Firestore reutilizável."""
    init_app()
    return firestore.client()


def resolve_db(db=None):
    """Retorna o db injetado (testes) ou o cliente real."""
    return db if db is not None else get_db()
