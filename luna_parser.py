"""
LUNA — Camada de Inteligência (AI Layer)
Arquivo: luna_parser.py
"""

from openai import OpenAI
import json
import re

OPENAI_API_KEY = "COLE_SUA_CHAVE_AQUI"

SYSTEM_PROMPT = """
Você é o módulo de parsing semântico da Luna, uma IA especializada
em gerar modelos 3D funcionais para impressão 3D.

Sua única função é: receber uma descrição em linguagem natural de um
objeto funcional e retornar um JSON com os parâmetros geométricos
necessários para gerar esse objeto no Blender.

REGRAS OBRIGATÓRIAS:
1. Retorne APENAS JSON válido, sem texto antes ou depois.
2. Sempre inclua todos os campos, mesmo que use os valores padrão.
3. Aplique as regras de engenharia abaixo automaticamente.

REGRAS DE ENGENHARIA:
- espessura mínima de qualquer parede: 0.8 mm
- overhang máximo sem suporte: 45 graus
- "reforçado" → aumentar espessura em 30%
- "leve" ou "fino" → reduzir espessura ao mínimo seguro

OBJETOS SUPORTADOS:

suporte_celular:
{
  "objeto": "suporte_celular",
  "largura_dispositivo": <float, mm, padrão 78.0>,
  "profundidade_base": <float, mm, padrão 90.0>,
  "altura_trava": <float, mm, padrão 18.0>,
  "angulo_inclinacao": <float, graus, padrão 20.0>,
  "espessura_base": <float, mm, padrão 5.0>,
  "espessura_apoio": <float, mm, padrão 4.0>,
  "comprimento_apoio": <float, mm, padrão 70.0>,
  "tem_reforco": <bool, padrão true>,
  "notas": "<string>"
}

carregador_miband6:
{
  "objeto": "carregador_miband6",
  "espessura_base": <float, mm, padrão 4.0>,
  "altura_total": <float, mm, padrão 55.0>,
  "espessura_parede": <float, mm, padrão 3.5>,
  "diametro_cabo": <float, mm, padrão 4.0>,
  "tem_passagem_cabo": <bool, padrão true>,
  "notas": "<string>"
}

suporte_headphone:
{
  "objeto": "suporte_headphone",
  "largura_arco": <float, mm, padrão 200.0>,
  "altura_total": <float, mm, padrão 180.0>,
  "espessura_base": <float, mm, padrão 5.0>,
  "largura_base": <float, mm, padrão 120.0>,
  "profundidade_base": <float, mm, padrão 80.0>,
  "espessura_braco": <float, mm, padrão 12.0>,
  "altura_braco": <float, mm, padrão 130.0>,
  "largura_arco_topo": <float, mm, padrão 180.0>,
  "espessura_arco": <float, mm, padrão 15.0>,
  "tem_reforco": <bool, padrão true>,
  "notas": "<string>"
}

porta_cartao:
{
  "objeto": "porta_cartao",
  "largura_cartao": <float, mm, padrão 92.0>,
  "altura_cartao": <float, mm, padrão 57.0>,
  "capacidade_cartoes": <int, quantidade, padrão 20>,
  "angulo_inclinacao": <float, graus, padrão -30.0>,
  "espessura_base": <float, mm, padrão 4.0>,
  "espessura_parede": <float, mm, padrão 3.0>,
  "profundidade_slot": <float, mm, padrão 15.0>,
  "tem_reforco": <bool, padrão true>,
  "notas": "<string>"
}

Se o objeto não for suportado, retorne:
{"erro": "objeto_nao_suportado", "mensagem": "<explicação>"}
"""


def interpretar_prompt(texto_usuario: str) -> dict:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print(f"[Luna Parser] Interpretando: '{texto_usuario}'")

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": texto_usuario}
        ],
        temperature=0.2
    )

    resposta_texto = resposta.choices[0].message.content.strip()
    resposta_texto = re.sub(r"```json|```", "", resposta_texto).strip()

    try:
        parametros = json.loads(resposta_texto)
        print(f"[Luna Parser] ✅ Parâmetros extraídos com sucesso!")
        print(json.dumps(parametros, indent=2, ensure_ascii=False))
        return parametros
    except json.JSONDecodeError as e:
        print(f"[Luna Parser] ERRO: {e}")
        return {"erro": "parse_falhou", "resposta_bruta": resposta_texto}


if __name__ == "__main__":
    testes = [
        "porta cartão de visita inclinado para vários cartões",
        "suporte headphone",
        "suporte de celular reforçado",
    ]
    for prompt in testes:
        print("\n" + "="*50)
        resultado = interpretar_prompt(prompt)
        print(f"Objeto: {resultado.get('objeto', 'erro')}")
