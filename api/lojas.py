"""Uma conexão GestãoClick, lojas distintas e somente cadastro futuro de NF-e."""

from dataclasses import dataclass
from urllib.parse import urlsplit

from config import settings
from services.regras_fiscais import validar_escolhas_manuais


class IntegracaoFiscalPendente(RuntimeError):
    """Bloqueia qualquer operação real até o contrato e a autorização serem validados."""


@dataclass(frozen=True, repr=False)
class CredenciaisAPI:
    """Guarda uma única credencial sem expor segredos em representação ou logs."""

    url_base: str
    access_token: str
    secret_access_token: str

    def validar(self):
        """Exige HTTPS oficial; nenhum endpoint ou payload fiscal é presumido."""
        parsed = urlsplit(self.url_base)
        host = (parsed.hostname or '').lower()
        oficial = any(host == d or host.endswith('.' + d) for d in ('gestaoclick.com', 'gestaoclick.com.br'))
        if not oficial or parsed.scheme != 'https' or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.port not in (None, 443):
            raise ValueError('A API exige HTTPS oficial conferido no OpenAPI.')
        if any(not isinstance(s, str) or not s.strip() or any(c.isspace() for c in s) for s in (self.access_token, self.secret_access_token)):
            raise ValueError('Credenciais protegidas da API única ausentes ou inválidas.')

    def __repr__(self):
        """Evita inclusive a impressão incidental da URL configurada."""
        return 'CredenciaisAPI(segredos=ocultos)'


@dataclass(frozen=True)
class LojasFiscais:
    """IDs devem vir do OpenAPI e da conta autorizada, nunca do nome ou CNPJ."""

    origem_id: str
    destino_id: str

    def validar(self):
        """Impede contexto ausente, ambíguo ou origem igual ao destino."""
        if any(not isinstance(v, str) or not v.strip() or len(v) > 120 for v in (self.origem_id, self.destino_id)) or self.origem_id == self.destino_id:
            raise ValueError('Valide os IDs distintos de FLT Comércio e Flagship - Flatter.')


class LeitorFLTComercio:
    """Consulta apenas a loja de origem; não oferece métodos de escrita."""

    def __init__(self, credenciais, lojas):
        """Mantém a mesma conexão e o escopo explícito da loja de origem."""
        self.credenciais, self.lojas = credenciais, lojas

    def buscar_pedidos_pendentes(self):
        """A consulta real permanece bloqueada até conferir o contrato da API."""
        raise IntegracaoFiscalPendente('Consulta da FLT Comércio depende do OpenAPI e do ID da loja.')


class CadastradorFlagship:
    """Prevê somente NF-e direta na loja de destino; não possui emitir_nota."""

    def __init__(self, credenciais, lojas):
        """Não cria cliente, produto, pedido ou venda no varejo."""
        self.credenciais, self.lojas = credenciais, lojas

    def criar_nota(self, dados):
        """Cadastro real ainda bloqueado; confirmar na API que não emite nem vende."""
        if not settings.NFE_CADASTRO_REAL_HABILITADO:
            raise IntegracaoFiscalPendente('Cadastro real desabilitado. Somente DEMO.')
        validar_escolhas_manuais(dados.get('opcoes_fiscais_manuais') if isinstance(dados, dict) else None)
        raise IntegracaoFiscalPendente('Cadastro direto sem venda depende do OpenAPI, mapeamento e autorização.')

    def consultar_nota(self, identificador):
        """Consulta futura será somente leitura, inclusive para reconciliação."""
        raise IntegracaoFiscalPendente('Consulta da Flagship - Flatter depende do OpenAPI.')


class ProvedorPorLojas:
    """Compartilha uma conexão, preservando responsabilidades e IDs das lojas."""

    origem = 'gestaoclick'
    ambiente = 'producao'

    def __init__(self, credenciais=None, lojas=None):
        """Não aceita fallback silencioso para as duas credenciais antigas."""
        self.credenciais = credenciais or CredenciaisAPI(settings.GESTAOCLICK_API_BASE_URL, settings.GESTAOCLICK_API_ACCESS_TOKEN, settings.GESTAOCLICK_API_SECRET_ACCESS)
        self.lojas = lojas or LojasFiscais(settings.GESTAOCLICK_LOJA_ATACADO_ID, settings.GESTAOCLICK_LOJA_VAREJO_ID)
        self.credenciais.validar()
        self.lojas.validar()
        self.leitor = LeitorFLTComercio(self.credenciais, self.lojas)
        self.cadastrador = CadastradorFlagship(self.credenciais, self.lojas)

    def buscar_pedidos_pendentes(self):
        """Encaminha somente consultas à loja FLT Comércio."""
        return self.leitor.buscar_pedidos_pendentes()

    def criar_nota(self, dados):
        """Encaminha somente o cadastro futuro da nota, sem venda ou emissão."""
        return self.cadastrador.criar_nota(dados)

    def emitir_nota(self, _identificador):
        """Compatibilidade defensiva: emitir é sempre proibido, independentemente de flags."""
        raise IntegracaoFiscalPendente('Emissão exclusivamente manual no GestãoClick. Automação não emite.')
