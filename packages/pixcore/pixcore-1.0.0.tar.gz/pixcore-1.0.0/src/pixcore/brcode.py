from . import constants as const
from . import exceptions
from . import utils
from .models import PixData
from PIL import Image
import qrcode

class Pix:
    """
    Classe principal para a geração do payload e do QR Code para pagamentos Pix.

    Esta classe encapsula toda a lógica necessária para criar um BR Code Pix
    em conformidade com as especificações do Banco Central do Brasil.
    Permite a geração do payload em formato string e a criação de uma imagem
    de QR Code customizável.

    Parameters:
        pix_data (PixData): Objeto do tipo PixData contendo todas as informações necessárias para a geração do Pix.
    """
    def __init__(self, pix_data: PixData):
        self.pix_data = pix_data

    def _build_merchant_account_info(self) -> str:
        gui = utils.format_tlv(const.ID_GUI, const.GUI_BR_BCB_PIX)
        pix_key = utils.format_tlv(const.ID_PIX_KEY, self.pix_data.pix_key)
        
        value = f"{gui}{pix_key}"
        
        return utils.format_tlv(const.ID_MERCHANT_ACCOUNT_INFORMATION, value)

    def _build_additional_data(self) -> str:
        txid = utils.format_tlv(const.ID_TRANSACTION_ID, self.pix_data.transacao_id)
        return utils.format_tlv(const.ID_ADDITIONAL_DATA_FIELD_TEMPLATE, txid)

    def _build_language_template(self) -> str:
        parts = []
        if self.pix_data.idioma_preferencia:
            parts.append(utils.format_tlv(const.ID_LANGUAGE_PREFERENCE, self.pix_data.idioma_preferencia))
        if self.pix_data.recebedor_nome_alt:
            parts.append(utils.format_tlv(const.ID_MERCHANT_NAME_ALT, self.pix_data.recebedor_nome_alt))
        if self.pix_data.recebedor_cidade_alt:
            parts.append(utils.format_tlv(const.ID_MERCHANT_CITY_ALT, self.pix_data.recebedor_cidade_alt))
        
        if not parts:
            return ""

        return utils.format_tlv(const.ID_MERCHANT_INFO_LANGUAGE_TEMPLATE, "".join(parts))

    def payload(self) -> str:
        """
        Gera o payload completo do BR Code no formato TLV (Copia e Cola).

        O payload é a string que será codificada no QR Code, contendo todas as
        informações da transação formatadas segundo o padrão EMV® QRCPS.

        Returns:
            str: O payload completo e formatado, incluindo o CRC16.

        Examples:
            >>> pix_data = PixData(...)
            >>> pix_generator = Pix(pix_data)
            >>> br_code = pix_generator.payload()
            >>> print(br_code)
            '00020126580014br.gov.bcb.pix0136123e4567-e89b-12d3-a456-426655440000520400005303986540510.005802BR5913NOME DO LOJA6008SAO PAULO62290525txid-gerado-pelo-sistema63041A29'
        """
        payload_parts = [
            utils.format_tlv(const.ID_PAYLOAD_FORMAT_INDICATOR, const.PAYLOAD_FORMAT_INDICATOR_VALUE),
        ]

        if self.pix_data.ponto_iniciacao_metodo:
            payload_parts.append(utils.format_tlv(const.ID_POINT_OF_INITIATION_METHOD, self.pix_data.ponto_iniciacao_metodo))

        payload_parts.extend([
            self._build_merchant_account_info(),
            utils.format_tlv(const.ID_MERCHANT_CATEGORY_CODE, self.pix_data.receptor_categoria_code),
            utils.format_tlv(const.ID_TRANSACTION_CURRENCY, const.TRANSACTION_CURRENCY_BRL),
        ])

        if self.pix_data.valor:
            amount_str = f"{self.pix_data.valor:.2f}"
            payload_parts.append(utils.format_tlv(const.ID_TRANSACTION_AMOUNT, amount_str))

        payload_parts.extend([
            utils.format_tlv(const.ID_COUNTRY_CODE, const.COUNTRY_CODE_BR),
            utils.format_tlv(const.ID_MERCHANT_NAME, self.pix_data.recebedor_nome),
            utils.format_tlv(const.ID_MERCHANT_CITY, self.pix_data.recebedor_cidade),
        ])

        if self.pix_data.recebedor_cep:
            payload_parts.append(utils.format_tlv(const.ID_POSTAL_CODE, self.pix_data.recebedor_cep))

        payload_parts.extend([
            self._build_additional_data(),
            self._build_language_template()
        ])
        
        payload = "".join(filter(None, payload_parts))
        
        crc = utils.calculate_crc16(payload + const.ID_CRC16 + "04")
        payload += utils.format_tlv(const.ID_CRC16, crc)
        
        return payload
    
    def qrcode(self, caminho_logo: str = None, cor_qr: str = "black", cor_fundo: str = "white", box_size: int = 10, border: int = 4) -> Image.Image:
        """
        Gera um objeto de imagem (Pillow) do QR Code a partir do payload.

        Args:
            caminho_logo (str, optional): O caminho para um arquivo de imagem (ex: .png)
                                          a ser centralizado no QR Code. Defaults to None.
            cor_qr (str, optional): A cor dos módulos do QR Code. Pode ser um nome de cor
                                    (ex: "navy") ou um código hexadecimal (ex: "#000080").
                                    Defaults to "black".
            cor_fundo (str, optional): A cor de fundo do QR Code. Defaults to "white".
            box_size (int, optional): O tamanho em pixels de cada "box" do QR Code. Defaults to 10.
            border (int, optional): A largura da borda em "boxes". Defaults to 4.

        Returns:
            Image.Image: Um objeto de imagem da biblioteca Pillow contendo o QR Code.

        Raises:
            exceptions.ProcessamentoImagemError: Se ocorrer um erro ao processar o
                                                 arquivo de logo (ex: não encontrado, corrompido).
        """
        payload_str = self.payload()
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(payload_str)
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color=cor_qr, back_color=cor_fundo).convert('RGB')

        if caminho_logo:
            try:
                logo = Image.open(caminho_logo)
                tamanho_max_logo = int(img_qr.size[0] * 0.25)
                logo.thumbnail((tamanho_max_logo, tamanho_max_logo))
                
                pos_x = (img_qr.size[0] - logo.size[0]) // 2
                pos_y = (img_qr.size[1] - logo.size[1]) // 2
                
                img_qr.paste(logo, (pos_x, pos_y), mask=logo)
            except FileNotFoundError:
                raise exceptions.ProcessamentoImagemError(
                    caminho_imagem=caminho_logo,
                    motivo="Arquivo não encontrado."
                ) from None
            
            except Exception as e:
                # Erro genérico de processamento.
                raise exceptions.ProcessamentoImagemError(
                    caminho_imagem=caminho_logo,
                    motivo=f"Erro desconhecido ao processar o logo: {e}"
                ) from e
        
        return img_qr
    
    def save_qrcode(self, caminho_arquivo_saida: str, caminho_logo: str = None, cor_qr: str = "black", cor_fundo: str = "white", box_size: int = 10, border: int = 4):
        """
        Gera e salva a imagem do QR Code diretamente em um arquivo.

        Args:
            caminho_arquivo_saida (str): O caminho e nome do arquivo onde a imagem
                                         do QR Code será salva (ex: 'output/pix.png').
            caminho_logo (str, optional): O caminho para um arquivo de imagem a ser
                                          centralizado no QR Code. Defaults to None.
            cor_qr (str, optional): A cor dos módulos do QR Code. Defaults to "black".
            cor_fundo (str, optional): A cor de fundo do QR Code. Defaults to "white".
            box_size (int, optional): O tamanho em pixels de cada "box" do QR Code. Defaults to 10.
            border (int, optional): A largura da borda em "boxes". Defaults to 4.
        
        Raises:
            exceptions.ErroDeESError: Se ocorrer um erro ao salvar o arquivo
                                      (ex: permissão negada, caminho inválido).
            exceptions.ProcessamentoImagemError: Se ocorrer um erro ao processar o
                                                 arquivo de logo.

        Examples:
            >>> pix_data = PixData(...)
            >>> pix_generator = Pix(pix_data)
            >>> pix_generator.save_qrcode("meu_pix_qr.png", caminho_logo="logo.png")
        """
        try:
            imagem_qr = self.qrcode(
                caminho_logo=caminho_logo, 
                cor_qr=cor_qr, 
                cor_fundo=cor_fundo,
                box_size=box_size,
                border=border
            )
            imagem_qr.save(caminho_arquivo_saida)
            return True
        except (IOError, PermissionError) as e:
            raise exceptions.ErroDeESError(
                caminho_arquivo=caminho_arquivo_saida,
                motivo=f"Não foi possível salvar o arquivo. Verifique as permissões. Erro original: {e}"
            ) from e
        except Exception as e:
            raise exceptions.ErroDeESError(
                caminho_arquivo=caminho_arquivo_saida,
                motivo=f"Ocorreu um erro inesperado ao salvar o QR Code: {e}"
            ) from e