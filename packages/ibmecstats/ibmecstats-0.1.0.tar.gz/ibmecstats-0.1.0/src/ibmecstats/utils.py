import numpy as np

def calcular_estatisticas_descritivas(dados):
    """
    Calcula e retorna estatísticas descritivas básicas de um conjunto de dados.
    
    Args:
        dados (array-like): Um array ou lista de números.
        
    Returns:
        dict: Um dicionário contendo n, média, desvio padrão e variância.
    """
    dados = np.asarray(dados)
    media = np.mean(dados)
    desvio_padrao = np.std(dados, ddof=1)  # ddof=1 para desvio padrão amostral
    variancia = np.var(dados, ddof=1)    # ddof=1 para variância amostral
    n = len(dados)
    return {
        'n': n, 
        'media': media, 
        'desvio_padrao': desvio_padrao, 
        'variancia': variancia
    }

def ordenar_dados(dados):
    """
    Retorna os dados ordenados em ordem crescente.
    
    Args:
        dados (array-like): Um array ou lista de números.
        
    Returns:
        np.ndarray: Um array numpy com os dados ordenados.
    """
    return np.sort(np.asarray(dados))

def padronizar_dados(dados):
    """
    Padroniza os dados para terem média 0 e desvio padrão 1 (Z-score).
    
    Args:
        dados (array-like): Um array ou lista de números.
        
    Returns:
        np.ndarray: Um array numpy com os dados padronizados.
    """
    dados = np.asarray(dados)
    stats = calcular_estatisticas_descritivas(dados)
    media = stats['media']
    desvio_padrao = stats['desvio_padrao']
    
    if desvio_padrao == 0:
        # Evita divisão por zero se todos os dados forem iguais
        return np.zeros_like(dados)
        
    return (dados - media) / desvio_padrao
