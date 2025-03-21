
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def preencher_escala_otimizado(escala, disponibilidade, inspetores, preferencias, max_escalas=7):
    try:
        disponibilidade["Inspetor"] = disponibilidade["Inspetor"].str.strip().str.upper()
        inspetores["Inspetor"] = inspetores["Inspetor"].str.strip().str.upper()
        preferencias = {k.strip().upper(): v.strip().upper() for k, v in preferencias.items()}

        for df in [escala, disponibilidade]:
            df["Semana"] = pd.to_datetime(df["Semana"], format="%d/%m/%Y", errors="coerce")

        escala["Inspetor 1"] = ""
        escala["Inspetor 2"] = ""

        historico_escalas = {insp: set() for insp in inspetores["Inspetor"]}
        tipos_validos = {"Sólidos", "Medicamentos", "Estéreis", "Insumos", "Biológicos"}

        disponibilidade = disponibilidade.merge(inspetores, on="Inspetor", how="inner")

        for i, row in escala.iterrows():
            semana, tipo, regiao = row["Semana"], row["Tipo"], row["Região"]

            if pd.isna(semana) or pd.isna(tipo) or tipo not in tipos_validos:
                logger.debug(f"Linha {i} ignorada: dados inválidos.")
                continue

            semana_str = semana.strftime("%d/%m/%Y")
            semana_anterior = (semana - pd.Timedelta(days=7)).strftime("%d/%m/%Y")

            inspetores_disponiveis = disponibilidade[disponibilidade["Semana"] == semana]
            if inspetores_disponiveis.empty:
                logger.debug(f"Semana {semana_str}: nenhum inspetor disponível.")
                continue

            lideres = inspetores_disponiveis[inspetores_disponiveis["Liderança"] == "Líder"]["Inspetor"].tolist()
            nao_lideres = inspetores_disponiveis[inspetores_disponiveis["Liderança"] == "Não Líder"]["Inspetor"].tolist()

            candidatos = [insp for insp in lideres + nao_lideres if len(historico_escalas[insp]) < max_escalas]

            if regiao != "C":
                candidatos = [insp for insp in candidatos if semana_anterior not in historico_escalas[insp]]

            logger.debug(f"Semana {semana_str} / Região {regiao} / Candidatos: {candidatos}")

            if len(candidatos) < 2:
                logger.debug(f"Semana {semana_str}: candidatos insuficientes.")
                continue

            candidatos = sorted(candidatos, key=lambda x: len(historico_escalas[x]))
            inspetor_1 = candidatos[0]

            parceiro_preferido = preferencias.get(inspetor_1, "")
            if parceiro_preferido in candidatos:
                inspetor_2 = parceiro_preferido
            else:
                inspetor_2 = candidatos[1] if len(candidatos) > 1 else ""

            if not (inspetor_1 in lideres or inspetor_2 in lideres):
                lider_disponivel = [insp for insp in lideres if insp in candidatos]
                if lider_disponivel:
                    inspetor_1 = lider_disponivel[0]

            historico_escalas[inspetor_1].add(semana_str)
            if inspetor_2:
                historico_escalas[inspetor_2].add(semana_str)

            escala.at[i, "Inspetor 1"] = inspetor_1
            escala.at[i, "Inspetor 2"] = inspetor_2

        logger.debug("Escala preenchida com sucesso")
        return escala, gerar_estatisticas(escala)

    except Exception as e:
        logger.error(f"Erro ao preencher escala: {e}")
        raise

def gerar_estatisticas(escala):
    try:
        estatisticas = escala.melt(value_vars=["Inspetor 1", "Inspetor 2"], var_name="Função", value_name="Inspetor")
        estatisticas = estatisticas.groupby("Inspetor").size().reset_index(name="Frequência")
        logger.debug("Estatísticas geradas com sucesso")
        return estatisticas
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {e}")
        raise
