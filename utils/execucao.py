"""Bloqueio local para impedir duas execuções simultâneas da automação."""

import os
from contextlib import contextmanager

from config.settings import CAMINHO_LOCK


class ExecucaoJaAtiva(RuntimeError):
    pass


def _bloquear_arquivo(arquivo):
    arquivo.seek(0)

    if os.name == "nt":
        import msvcrt

        if arquivo.read(1) == "":
            arquivo.seek(0)
            arquivo.write("0")
            arquivo.flush()

        arquivo.seek(0)
        msvcrt.locking(
            arquivo.fileno(),
            msvcrt.LK_NBLCK,
            1
        )
        return

    import fcntl

    fcntl.flock(
        arquivo.fileno(),
        fcntl.LOCK_EX | fcntl.LOCK_NB
    )


def _desbloquear_arquivo(arquivo):
    arquivo.seek(0)

    if os.name == "nt":
        import msvcrt

        msvcrt.locking(
            arquivo.fileno(),
            msvcrt.LK_UNLCK,
            1
        )
        return

    import fcntl

    fcntl.flock(
        arquivo.fileno(),
        fcntl.LOCK_UN
    )


@contextmanager
def bloqueio_execucao():
    CAMINHO_LOCK.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo = CAMINHO_LOCK.open(
        "a+",
        encoding="utf-8"
    )

    try:
        try:
            _bloquear_arquivo(
                arquivo
            )
        except OSError as erro:
            raise ExecucaoJaAtiva(
                "Já existe outra execução ativa nesta máquina."
            ) from erro

        yield
    finally:
        try:
            _desbloquear_arquivo(
                arquivo
            )
        finally:
            arquivo.close()
