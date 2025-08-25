from typing import Generator, Tuple
from . import exceptions

def format_tlv(id_field: str, value: str) -> str:
    """
    Formata um campo no padrão TLV (Type-Length-Value).

    O formato TLV é composto por:
    - ID (Type): Identificador do campo (2 dígitos).
    - Length: Tamanho do valor (2 dígitos).
    - Value: O dado em si.

    Args:
        id_field (str): O identificador do campo (ID ou "Tag").
        value (str): O valor do campo.

    Returns:
        str: A string formatada em TLV. Ex: "5913NOME DO LOJA".

    Examples:
        >>> format_tlv("59", "EMPRESA MODELO")
        '5914EMPRESA MODELO'
        >>> format_tlv("53", "986")
        '5303986'
    """
    length = str(len(value)).zfill(2)
    return f"{id_field}{length}{value}"

def calculate_crc16(payload: str) -> str:
    """
    Calcula o checksum CRC16-CCITT do payload.

    O cálculo é realizado conforme o padrão EMV® QRCPS, que utiliza o polinômio
    0x1021 e valor inicial 0xFFFF. O resultado é uma string hexadecimal de 4
    caracteres.

    Args:
        payload (str): O payload completo (sem o campo do CRC) para o qual o
                       checksum será calculado.

    Returns:
        str: O checksum CRC16 calculado, formatado como uma string hexadecimal
             de 4 caracteres maiúsculos.

    Examples:
        >>> payload_exemplo = "00020126360014BR.GOV.BCB.PIX0114+5561999999999520400005303986540510.005802BR5913FULANO DE TAL6008BRASILIA62070503***6304"
        >>> calculate_crc16(payload_exemplo)
        'E3A2'
    """
    crc = 0xFFFF
    polynomial = 0x1021

    for byte in payload.encode('utf-8'):
        crc ^= (byte << 8)
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
    
    return format(crc & 0xFFFF, 'X').zfill(4)

def parse_tlv(payload: str) -> Generator[Tuple[str, int, str], None, None]:
    """
    Parseia uma string de payload no formato TLV e retorna os campos.

    Esta função atua como um gerador, processando a string do payload
    de forma iterativa. A cada iteração, ela lê um campo completo (ID, Tamanho, Valor)
    e o retorna como uma tupla (ID, Tamanho, Valor).

    Args:
        payload (str): A string contendo múltiplos campos TLV concatenados.

    Yields:
        Generator[Tuple[str, int, str], None, None]: Uma tupla contendo (ID, Tamanho, Valor).
    
    Raises:
        exceptions.DecodificacaoPayloadError: Se a string de tamanho (length)
                                               não for um número válido, indicando
                                               um payload malformado.
    """
    index = 0
    while index < len(payload):
        id_field = payload[index : index + 2]
        index += 2

        length_str = payload[index : index + 2]
        index += 2
        
        try:
            value_length = int(length_str)
        except ValueError:
            raise exceptions.DecodificacaoPayloadError(
                f"Tamanho de campo inválido. Esperava um número, mas recebi '{length_str}'."
            ) from None

        value = payload[index : index + value_length]
        index += value_length

        yield (id_field, value_length,value)