"""
LUNA — Motor Geométrico v2.3
Arquivo: luna_geometry.py

Adicionado: porta_cartao
  Cartão padrão: 90 x 55mm
  Slot inclinado para vários cartões empilhados
"""

import bpy
import sys
import json
import math


def limpar_cena():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)


def criar_cubo_parametrico(nome, largura, altura, profundidade, posicao=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=posicao)
    obj = bpy.context.active_object
    obj.name = nome
    obj.scale = (largura / 2, profundidade / 2, altura / 2)
    bpy.ops.object.transform_apply(scale=True)
    return obj


def criar_prisma_inclinado(nome, largura, comprimento, espessura, angulo_graus, posicao=(0, 0, 0)):
    import bmesh
    angulo_rad = math.radians(angulo_graus)
    dy = -math.sin(angulo_rad)
    dz = math.cos(angulo_rad)
    w = largura / 2
    e = espessura / 2
    vertices = [
        (-w,  e, 0), ( w,  e, 0), ( w, -e, 0), (-w, -e, 0),
        (-w,  e + dy * comprimento, dz * comprimento),
        ( w,  e + dy * comprimento, dz * comprimento),
        ( w, -e + dy * comprimento, dz * comprimento),
        (-w, -e + dy * comprimento, dz * comprimento),
    ]
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)]
    mesh = bpy.data.meshes.new(nome + "_mesh")
    obj = bpy.data.objects.new(nome, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    verts_bm = [bm.verts.new(v) for v in vertices]
    bm.verts.ensure_lookup_table()
    for f in faces:
        bm.faces.new([verts_bm[i] for i in f])
    bm.to_mesh(mesh)
    bm.free()
    obj.location = posicao
    return obj


def recalcular_normais(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def aplicar_bevel(obj, largura=1.0, segmentos=3):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='BEVEL')
    obj.modifiers["Bevel"].width = largura
    obj.modifiers["Bevel"].segments = segmentos
    bpy.ops.object.modifier_apply(modifier="Bevel")


def unir_objetos(objetos, nome_final):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objetos:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objetos[0]
    bpy.ops.object.join()
    bpy.context.active_object.name = nome_final
    return bpy.context.active_object


# ─────────────────────────────────────────────
# SUPORTE DE CELULAR
# ─────────────────────────────────────────────

def gerar_suporte_celular(p):
    print("[Luna Geometry] Gerando suporte_celular...")
    largura=p["largura_dispositivo"]+4; profundidade=p["profundidade_base"]
    esp_base=p["espessura_base"]; esp_apoio=p["espessura_apoio"]
    comp_apoio=p["comprimento_apoio"]; angulo=p["angulo_inclinacao"]
    alt_trava=p["altura_trava"]; tem_reforco=p["tem_reforco"]
    objetos=[]
    objetos.append(criar_cubo_parametrico("base", largura=largura, altura=esp_base,
        profundidade=profundidade, posicao=(0,0,esp_base/2)))
    objetos.append(criar_prisma_inclinado("apoio", largura=largura, comprimento=comp_apoio,
        espessura=esp_apoio, angulo_graus=angulo,
        posicao=(0, profundidade/2-esp_apoio, esp_base)))
    objetos.append(criar_cubo_parametrico("trava", largura=largura, altura=alt_trava,
        profundidade=esp_base, posicao=(0,-profundidade/2+esp_base/2,esp_base+alt_trava/2)))
    if tem_reforco:
        for lado, x in [("esq",-(largura/2-esp_apoio/2)),("dir",(largura/2-esp_apoio/2))]:
            objetos.append(criar_cubo_parametrico(f"ref_{lado}",
                largura=esp_apoio*1.5, altura=alt_trava*0.6, profundidade=profundidade*0.3,
                posicao=(x,-profundidade/2+profundidade*0.15,esp_base+alt_trava*0.3)))
    modelo=unir_objetos(objetos,"suporte_celular_luna")
    recalcular_normais(modelo); aplicar_bevel(modelo,0.4,2); recalcular_normais(modelo)
    print("[Luna Geometry] ✅ suporte_celular gerado!")
    return modelo


# ─────────────────────────────────────────────
# CARREGADOR MI BAND 6
# ─────────────────────────────────────────────

def gerar_carregador_miband6(p):
    print("[Luna Geometry] Gerando carregador_miband6...")
    diam_cabo=p["diametro_cabo"]; esp_parede=p["espessura_parede"]
    larg_base=44.7; prof_base=50.0; alt_base=13.0
    larg_col=10.0; prof_col=19.0; alt_col=52.0
    larg_cab=32.0; prof_cab=47.0; alt_cab=10.5
    larg_canal=diam_cabo+2.0; prof_canal=diam_cabo+1.0; esp_canal=2.5
    objetos=[]
    objetos.append(criar_cubo_parametrico("base",largura=larg_base,altura=alt_base,profundidade=prof_base,posicao=(0,0,alt_base/2)))
    objetos.append(criar_cubo_parametrico("coluna",largura=larg_col,altura=alt_col,profundidade=prof_col,posicao=(0,0,alt_base+alt_col/2)))
    z_cab=alt_base+alt_col+alt_cab/2
    objetos.append(criar_cubo_parametrico("cabeca",largura=larg_cab,altura=alt_cab,profundidade=prof_cab,posicao=(0,0,z_cab)))
    z_canal=alt_base+alt_col/2; y_canal=-(prof_col/2+prof_canal/2)
    objetos.append(criar_cubo_parametrico("canal_esq",largura=esp_canal,altura=alt_col,profundidade=prof_canal,posicao=(-(larg_canal/2+esp_canal/2),y_canal,z_canal)))
    objetos.append(criar_cubo_parametrico("canal_dir",largura=esp_canal,altura=alt_col,profundidade=prof_canal,posicao=((larg_canal/2+esp_canal/2),y_canal,z_canal)))
    objetos.append(criar_cubo_parametrico("canal_fundo",largura=larg_canal+esp_canal*2,altura=alt_col,profundidade=esp_canal,posicao=(0,y_canal-prof_canal/2-esp_canal/2,z_canal)))
    modelo=unir_objetos(objetos,"carregador_miband6_luna")
    recalcular_normais(modelo); aplicar_bevel(modelo,1.0,3); recalcular_normais(modelo)
    print("[Luna Geometry] ✅ carregador_miband6 gerado!")
    return modelo


# ─────────────────────────────────────────────
# SUPORTE HEADPHONE
# ─────────────────────────────────────────────

def gerar_suporte_headphone(p):
    print("[Luna Geometry] Gerando suporte_headphone...")
    larg_base=p["largura_base"]; prof_base=p["profundidade_base"]
    esp_base=p["espessura_base"]; alt_braco=p["altura_braco"]
    esp_braco=p["espessura_braco"]; larg_arco=p["largura_arco_topo"]
    esp_arco=p["espessura_arco"]; tem_reforco=p["tem_reforco"]
    objetos=[]
    objetos.append(criar_cubo_parametrico("base",largura=larg_base,altura=esp_base,profundidade=prof_base,posicao=(0,0,esp_base/2)))
    objetos.append(criar_cubo_parametrico("coluna",largura=esp_braco,altura=alt_braco,profundidade=esp_braco,posicao=(0,0,esp_base+alt_braco/2)))
    z_arco=esp_base+alt_braco+esp_arco/2
    objetos.append(criar_cubo_parametrico("arco",largura=larg_arco,altura=esp_arco,profundidade=esp_braco*1.5,posicao=(0,0,z_arco)))
    for lado,x in [("aba_esq",-(larg_arco/2-esp_braco/2)),("aba_dir",(larg_arco/2-esp_braco/2))]:
        objetos.append(criar_cubo_parametrico(lado,largura=esp_braco,altura=esp_arco+8,profundidade=esp_braco*2,posicao=(x,0,z_arco-4)))
    if tem_reforco:
        for lado,y in [("ref_f",-(prof_base*0.2)),("ref_b",(prof_base*0.2))]:
            objetos.append(criar_cubo_parametrico(lado,largura=esp_braco*2.5,altura=alt_braco*0.25,profundidade=esp_braco,posicao=(0,y,esp_base+alt_braco*0.125)))
    modelo=unir_objetos(objetos,"suporte_headphone_luna")
    recalcular_normais(modelo); aplicar_bevel(modelo,1.2,3); recalcular_normais(modelo)
    print("[Luna Geometry] ✅ suporte_headphone gerado!")
    return modelo


# ─────────────────────────────────────────────
# PORTA CARTÃO DE VISITA
# ─────────────────────────────────────────────

def gerar_porta_cartao(p):
    """
    Porta cartão de visita inclinado para vários cartões empilhados.

    Estrutura:
      - Base sólida
      - Parede traseira inclinada (apoia os cartões)
      - Trava frontal baixa (segura os cartões)
      - Paredes laterais (evita cartões escaparem)

    Cartão padrão: 90 x 55mm
    Slot com folga para ~20 cartões empilhados
    """
    print("[Luna Geometry] Gerando porta_cartao...")

    larg_cartao  = p["largura_cartao"]       # 92mm (cartão + folga)
    alt_cartao   = p["altura_cartao"]        # 57mm
    capacidade   = p["capacidade_cartoes"]   # 20 cartões
    angulo       = p["angulo_inclinacao"]    # 70° (quase vertical)
    esp_base     = p["espessura_base"]       # 4mm
    esp_parede   = p["espessura_parede"]     # 3mm
    prof_slot    = p["profundidade_slot"]    # 15mm (profundidade do slot)
    tem_reforco  = p["tem_reforco"]

    # Espessura do slot = capacidade × 0.5mm por cartão
    esp_slot     = max(capacidade * 0.5, 8.0)  # mínimo 8mm

    # Dimensões da base
    larg_base    = larg_cartao + esp_parede * 2
    prof_base    = prof_slot + esp_parede * 3

    # Altura da parede traseira (baseada no cartão + ângulo)
    alt_parede   = alt_cartao * 0.85

    objetos = []

    # ── 1. BASE ──
    base = criar_cubo_parametrico("base",
        largura=larg_base,
        altura=esp_base,
        profundidade=prof_base,
        posicao=(0, 0, esp_base / 2))
    objetos.append(base)

    # Referências de posição Y
    y_tras  =  prof_base / 2 - esp_parede   # parede traseira no fundo
    y_front = -prof_base / 2 + esp_parede / 2   # trava frontal na borda da frente

    # ── 2. PAREDE TRASEIRA INCLINADA ──
    parede_tras = criar_prisma_inclinado("parede_traseira",
        largura=larg_cartao,
        comprimento=alt_parede,
        espessura=esp_parede,
        angulo_graus=angulo,
        posicao=(0, y_tras, esp_base))
    objetos.append(parede_tras)

    # ── 3. FUNDO DO SLOT ──
    fundo = criar_cubo_parametrico("fundo_slot",
        largura=larg_cartao,
        altura=esp_parede,
        profundidade=prof_base - esp_parede * 2,
        posicao=(0, 0, esp_base + esp_parede / 2))
    objetos.append(fundo)

    # ── 4. TRAVA FRONTAL ──
    alt_trava = 20.0
    trava = criar_cubo_parametrico("trava_frontal",
        largura=50.0,
        altura=alt_trava,
        profundidade=esp_parede,
        posicao=(0, y_front, esp_base + alt_trava / 2))
    objetos.append(trava)

    # ── 5. PAREDES LATERAIS ──
    for lado, x in [("lat_esq", -(larg_cartao / 2 + esp_parede / 2)),
                    ("lat_dir",  (larg_cartao / 2 + esp_parede / 2))]:
        lateral = criar_cubo_parametrico(lado,
            largura=esp_parede,
            altura=alt_parede * 0.6,
            profundidade=prof_base - esp_parede * 2,
            posicao=(x, 0, esp_base + alt_parede * 0.3))
        objetos.append(lateral)

    # ── 6. REFORÇOS ──
    if tem_reforco:
        for lado, x in [("ref_esq", -(larg_base / 2 - esp_parede)),
                        ("ref_dir",  (larg_base / 2 - esp_parede))]:
            reforco = criar_cubo_parametrico(lado,
                largura=esp_parede * 1.5,
                altura=esp_base * 2,
                profundidade=prof_base * 0.4,
                posicao=(x, 0, esp_base))
            objetos.append(reforco)

    # ── 7. UNIR + FINALIZAR ──
    modelo = unir_objetos(objetos, "porta_cartao_luna")
    recalcular_normais(modelo)
    aplicar_bevel(modelo, largura=0.6, segmentos=2)
    recalcular_normais(modelo)

    print("[Luna Geometry] ✅ porta_cartao gerado!")
    return modelo


# ─────────────────────────────────────────────
# EXPORTAR STL
# ─────────────────────────────────────────────

def exportar_stl(caminho_saida):
    bpy.ops.object.select_all(action='SELECT')
    try:
        bpy.ops.wm.stl_export(filepath=caminho_saida, ascii_format=False)
    except Exception:
        bpy.ops.export_mesh.stl(filepath=caminho_saida)
    print(f"[Luna Geometry] STL exportado: {caminho_saida}")


def main():
    argv = sys.argv
    if "--" not in argv:
        print("[Luna Geometry] ERRO: Nenhum parâmetro recebido.")
        sys.exit(1)

    args_after = argv[argv.index("--") + 1:]
    parametros = json.loads(args_after[0])
    caminho_stl = args_after[1]

    limpar_cena()
    tipo = parametros.get("objeto")

    if tipo == "suporte_celular":
        gerar_suporte_celular(parametros)
    elif tipo == "carregador_miband6":
        gerar_carregador_miband6(parametros)
    elif tipo == "suporte_headphone":
        gerar_suporte_headphone(parametros)
    elif tipo == "porta_cartao":
        gerar_porta_cartao(parametros)
    else:
        print(f"[Luna Geometry] ERRO: Objeto '{tipo}' não implementado.")
        sys.exit(1)

    exportar_stl(caminho_stl)
    print("[Luna Geometry] ✅ Concluído com sucesso.")


if __name__ == "__main__":
    main()
