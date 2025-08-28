from flask import Flask, request, render_template_string
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)

QUESTIONS = {
    "LGPD": [
        {"question": "O escritório possui um responsável formal pela proteção de dados (DPO ou encarregado)?",
         "options": [(0, "Não existe responsável definido."), (3, "Responsável definido, mas com poucas atribuições."), (5, "DPO designado com responsabilidades claras e atuantes.")]},
        {"question": "Há políticas de privacidade e proteção de dados formalizadas e atualizadas?",
         "options": [(0, "Não há políticas documentadas."), (3, "Políticas básicas, pouco atualizadas."), (5, "Políticas completas, revisadas regularmente.")]},
        {"question": "Os processos de coleta, uso e armazenamento de dados pessoais são mapeados e controlados?",
         "options": [(0, "Não há mapeamento ou controles claros."), (3, "Mapeamento parcial e controles pontuais."), (5, "Mapeamento completo e controles rigorosos implementados.")]},
        {"question": "A equipe recebe treinamentos periódicos sobre LGPD e tratamento de dados?",
         "options": [(0, "Não realiza treinamentos."), (3, "Treinamentos pouco frequentes."), (5, "Treinamentos regulares e atualizados.")]},
        {"question": "O escritório possui processos para atender aos direitos dos titulares (acesso, correção, exclusão)?",
         "options": [(0, "Não possui processos definidos."), (3, "Processos definidos, mas não bem estruturados."), (5, "Processos formalizados, ágeis e efetivos.")]},
        {"question": "Há políticas e práticas para retenção e descarte seguro dos dados pessoais?",
         "options": [(0, "Ausência de políticas claras sobre retenção e descarte."), (3, "Políticas existentes, mas com execução irregular."), (5, "Políticas formais, com monitoramento e auditoria.")]}
    ],
    "CIS Controls": [
        {"question": "O escritório mantém um inventário atualizado e controlado de todo hardware conectado à rede? (CIS Control 1)",
         "options": [(0, "Não mantém inventário formal."), (3, "Inventário parcial ou desatualizado."), (5, "Inventário completo, atualizado e auditado regularmente.")]},
        {"question": "A lista de softwares autorizados e instalados é mantida e gerenciada para evitar software não autorizado? (CIS Control 2)",
         "options": [(0, "Sem controle ou registro de softwares."), (3, "Inventário parcial com pouca gestão."), (5, "Controle rigoroso com remoção de softwares não autorizados.")]},
        {"question": "Há processos estabelecidos para identificar, classificar e corrigir vulnerabilidades em sistemas e softwares usados? (CIS Control 3)",
         "options": [(0, "Não existem processos formais."), (3, "Processo ad hoc ou irregular."), (5, "Processo contínuo, automatizado e auditado.")]},
        {"question": "O acesso com privilégios elevados é restrito, monitorado e revisado periodicamente? (CIS Control 4)",
         "options": [(0, "Não existe controle ou revisão."), (3, "Controle parcial e revisão esporádica."), (5, "Controle rigoroso, revisão regular e uso mínimo do privilégio.")]},
        {"question": "Existem políticas e práticas para configuração segura padrão em sistemas operacionais e aplicativos? (CIS Control 5)",
         "options": [(0, "Configuração insegura e não padronizada."), (3, "Configurações básicas aplicadas, mas sem padronização completa."), (5, "Configurações rigorosas e auditadas com base em boas práticas reconhecidas.")]},
        {"question": "O escritório monitora, centraliza e analisa logs de eventos de rede e sistemas para detectar incidentes? (CIS Control 6)",
         "options": [(0, "Não há monitoramento ou centralização."), (3, "Monitoramento limitado e manual."), (5, "Monitoramento automático, análise em tempo real e resposta rápida.")]},
    ]
}

@app.route('/', methods=['GET'])
def form():
    html = '<h2>Formulário de Maturidade: LGPD e Cibersegurança (CIS Controls)</h2>'
    html += '<form method="post" action="/result">'
    for section, questions in QUESTIONS.items():
        html += f'<h3>{section}</h3>'
        for i, q in enumerate(questions):
            html += f'<p>{q["question"]}</p>'
            for val, opt in q["options"]:
                html += f'<input type="radio" name="{section}_{i}" value="{val}" required> {opt}<br>'
    html += '<br><input type="submit" value="Enviar"></form>'
    return render_template_string(html)

@app.route('/result', methods=['POST'])
def result():
    # Coleta e normaliza respostas por seção
    section_answers = {section: [] for section in QUESTIONS}
    for section, questions in QUESTIONS.items():
        for i in range(len(questions)):
            val = int(request.form.get(f'{section}_{i}', 0))
            section_answers[section].append(val)

    # Calcula pontuação total e percentuais médios por seção
    scores = {}
    percentages = {}
    for section, answers in section_answers.items():
        max_score = len(answers) * 5 if answers else 1
        total = sum(answers)
        scores[section] = total
        percentages[section] = round((total / max_score) * 100, 2)

    # Prepara dados por pergunta (normalizados para 0-100) para cada seção
    def normalize(values):
        return [(v / 5) * 100 for v in values]

    lgpd_values = normalize(section_answers.get('LGPD', []))
    cis_values = normalize(section_answers.get('CIS Controls', []))

    # Cria dois subplots polares (um por seção), com cores distintas
    fig, (ax_lgpd, ax_cis) = plt.subplots(1, 2, figsize=(12, 6), subplot_kw=dict(polar=True))

    def plot_radar(ax, values, color, title):
        if not values:
            values = [0]
        labels = [f'Q{i+1}' for i in range(len(values))]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        # fecha o polígono
        values_closed = values + values[:1]
        angles_closed = angles + angles[:1]

        ax.plot(angles_closed, values_closed, color=color, linewidth=2)
        ax.fill(angles_closed, values_closed, color=color, alpha=0.25)
        ax.set_xticks(angles)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 100)
        ax.set_yticklabels([])
        ax.set_title(title)

    plot_radar(ax_lgpd, lgpd_values, 'blue', 'LGPD')
    plot_radar(ax_cis, cis_values, 'red', 'CIS Controls')

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')

    report_json = {
        "scores": scores,
        "percentages": percentages,
        "answers": section_answers
    }

    html = '<h2>Resultado da Avaliação de Maturidade</h2>'
    html += f'<img src="data:image/png;base64,{img_str}" alt="Gráfico Radar"><br><br>'
    html += f'<pre>{report_json}</pre>'
    html += '<a href="/">Fazer nova avaliação</a>'
    return render_template_string(html)

if __name__ == '__main__':
    # Ajustar para ambiente WSGI do Vercel
    app.run()
