"""Roteador fechado de responsabilidades entre as DUAS contas GestãoClick.

A preparação abaixo não acessa a API real. Endpoints e campos fiscais precisam
ser confirmados no OpenAPI autorizado ANTES de implementar qualquer operação.
O Gerente de Estoque continua integralmente somente leitura.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

from config import settings


class IntegracaoFiscalPendente(RuntimeError):
    """Bloqueio seguro enquanto contrato fiscal e autorização não são validados."""


def _host_oficial(hostname: str | None) -> bool:
    host = (hostname or "").lower()
    return any(host == base or host.endswith("." + base)
               for base in ("gestaoclick.com", "gestaoclick.com.br"))


@dataclass(frozen=True, repr=False)
class CredenciaisConta:
    """Credenciais isoladas por conta, sem exposição em repr/log."""

    identificador: str
    url_base: str
    access_token: str
    secret_access_token: str

    def validar(self) -> None:
        endereco = urlsplit(self.url_base)
        if (endereco.scheme != "https" or not _host_oficial(endereco.hostname)
                or endereco.username or endereco.password or endereco.port not in (None, 443)
                or endereco.query or endereco.fragment):
            raise ValueError(
                f"Configuração inválida da conta {self.identificador}: "
                "use somente HTTPS e um domínio oficial conferido no OpenAPI."
            )
        if any(not isinstance(valor, str) or not valor.strip()
               for valor in (self.access_token, self.secret_access_token)):
            raise ValueError(
                f"Credenciais da conta {self.identificador} ausentes nos Secrets."
            )
        if any(any(c.isspace() for c in valor)
               for valor in (self.access_token, self.secret_access_token)):
            raise ValueError(f"Credenciais da conta {self.identificador} inválidas.")

    def __repr__(self) -> str:
        return f"CredenciaisConta(identificador={self.identificador!r}, segredos=ocultos)"


def credenciais_atacado() -> CredenciaisConta:
    return CredenciaisConta(
        "ATACADO",
        settings.GESTAOCLICK_ATACADO_BASE_URL,
        settings.GESTAOCLICK_ATACADO_ACCESS_TOKEN,
        settings.GESTAOCLICK_ATACADO_SECRET_ACCESS,
    )


def credenciais_varejo() -> CredenciaisConta:
    return CredenciaisConta(
        "VAREJO",
        settings.GESTAOCLICK_VAREJO_BASE_URL,
        settings.GESTAOCLICK_VAREJO_ACCESS_TOKEN,
        settings.GESTAOCLICK_VAREJO_SECRET_ACCESS,
    )


class LeitorAtacado:
    """Fonte exclusiva de pedidos. Nenhuma operação de escrita é exposta."""

    def __init__(self, credenciais: CredenciaisConta | None = None):
        self._credenciais = credenciais if credenciais is not None else credenciais_atacado()
        self._credenciais.validar()

    def buscar_pedidos_pendentes(self):
        raise IntegracaoFiscalPendente(
            "Consulta de pedidos do Atacado indisponível até validação de "
            "endpoints, status e campos no OpenAPI autorizado."
        )


class EmissorVarejo:
    """Único ponto possível de emissão fiscal (desativado por padrão)."""

    def __init__(self, credenciais: CredenciaisConta | None = None):
        self._credenciais = credenciais if credenciais is not None else credenciais_varejo()
        self._credenciais.validar()

    @staticmethod
    def _exigir_habilitacao():
        if not settings.NFE_EMISSAO_REAL_HABILITADA:
            raise IntegracaoFiscalPendente(
                "Emissão real desabilitada. Apenas simulação até validação fiscal."
            )

    def criar_nota(self, dados):
        self._exigir_habilitacao()
        raise IntegracaoFiscalPendente(
            "Criação da NF-e no Varejo ainda depende do contrato fiscal real, "
            "da checagem de duplicidade NO ERP e da aprovação explícita das regras."
        )

    def emitir_nota(self, id_externo):
        self._exigir_habilitacao()
        raise IntegracaoFiscalPendente(
            "Emissão ainda não implementada: confirmar endpoint e resposta no OpenAPI."
        )

    def consultar_nota(self, id_externo):
        raise IntegracaoFiscalPendente(
            "Consulta de NF-e do Varejo ainda depende do OpenAPI conferido."
        )

    def baixar_xml(self, id_externo):
        raise IntegracaoFiscalPendente("Download XML pendente de OpenAPI.")

    def baixar_pdf(self, id_externo):
        raise IntegracaoFiscalPendente("Download PDF pendente de OpenAPI.")


class ProvedorDuasContas:
    """Adapta o fluxo existente sem permitir escrita pelo Atacado.

    A injeção de leitor/emissor serve APENAS para testes com dublês; a execução
    produtiva instancia os adaptadores reais, atualmente fail-closed.
    """

    origem = "gestaoclick"
    ambiente = "producao"

    def __init__(self, leitor=None, emissor=None):
        self._leitor = leitor if leitor is not None else LeitorAtacado()
        self._emissor = emissor if emissor is not None else EmissorVarejo()

    def buscar_pedidos_pendentes(self):
        return self._leitor.buscar_pedidos_pendentes()

    def criar_nota(self, dados):
        return self._emissor.criar_nota(dados)

    def emitir_nota(self, id_externo):
        return self._emissor.emitir_nota(id_externo)

    def consultar_nota(self, id_externo):
        return self._emissor.consultar_nota(id_externo)

    def baixar_xml(self, id_externo):
        return self._emissor.baixar_xml(id_externo)

    def baixar_pdf(self, id_externo):
        return self._emissor.baixar_pdf(id_externo)
