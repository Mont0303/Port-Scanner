import socket
import threading
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("dark-blue")

servicos = {
    20: "FTP Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    8080: "HTTP Alternate",
}


def atualizar_widget(widget, metodo, *args, **kwargs):
    widget.after(0, lambda: getattr(widget, metodo)(*args, **kwargs))


def realizar_scan(ip, porta_inicio, porta_fim, text_area, btn_iniciar, btn_relatorio, progress_bar, label_pct):
    start_time = time.perf_counter()
    atualizar_widget(
        text_area,
        "insert",
        ctk.END,
        f"[*] Iniciando scan em {ip} (Portas {porta_inicio} a {porta_fim})...\n\n",
    )
    atualizar_widget(text_area, "see", ctk.END)

    total_portas = porta_fim - porta_inicio + 1
    portas_verificadas = 0

    for porta in range(porta_inicio, porta_fim + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            resultado = s.connect_ex((ip, porta))

            if resultado == 0:
                nome_servico = servicos.get(porta, "Serviço desconhecido")
                atualizar_widget(
                    text_area,
                    "insert",
                    ctk.END,
                    f"[+] Porta {porta} aberta - {nome_servico}\n",
                )
                atualizar_widget(text_area, "see", ctk.END)

            s.close()
        except Exception:
            pass

        portas_verificadas += 1
        if total_portas > 0:
            progresso = portas_verificadas / total_portas
            atualizar_widget(progress_bar, "set", progresso)
            atualizar_widget(label_pct, "configure", text=f"{int(progresso * 100)}%")

    end_time = time.perf_counter()
    atualizar_widget(
        text_area,
        "insert",
        ctk.END,
        f"\n[-] Scan finalizado. Tempo total: {end_time - start_time:.2f} segundos\n",
    )
    atualizar_widget(text_area, "insert", ctk.END, "---------------------------------------------------\n")
    atualizar_widget(text_area, "see", ctk.END)

    atualizar_widget(btn_iniciar, "configure", state="normal", text="Iniciar Scan")
    atualizar_widget(btn_relatorio, "configure", state="normal")


def iniciar_thread():
    ip = entry_ip.get()
    try:
        porta_inicio = int(entry_inicio.get())
        porta_fim = int(entry_fim.get())
    except ValueError:
        messagebox.showerror("Erro de Validação", "As portas devem ser números inteiros.")
        return

    if not ip.strip():
        messagebox.showerror("Erro de Validação", "Digite um endereço IP válido.")
        return

    if porta_inicio > porta_fim:
        messagebox.showerror(
            "Erro de Validação",
            "A porta inicial não pode ser maior que a porta final.",
        )
        return

    text_saida.delete("0.0", ctk.END)
    btn_scan.configure(state="disabled", text="Buscando...")
    btn_exportar.configure(state="disabled")
    progresso_bar.set(0.0)
    label_porcentagem.configure(text="0%")

    thread = threading.Thread(
        target=realizar_scan,
        args=(
            ip,
            porta_inicio,
            porta_fim,
            text_saida,
            btn_scan,
            btn_exportar,
            progresso_bar,
            label_porcentagem,
        ),
    )
    thread.daemon = True
    thread.start()


def salvar_relatorio():
    conteudo_relatorio = text_saida.get("0.0", ctk.END).strip()

    if not conteudo_relatorio or "[*] Iniciando scan" not in conteudo_relatorio:
        messagebox.showwarning(
            "Aviso",
            "Não há dados de scan válidos para exportar.",
        )
        return

    arquivo_destino = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[
            ("Arquivo de Texto", "*.txt"),
            ("Arquivo CSV", "*.csv"),
            ("Todos os arquivos", "*.*"),
        ],
        title="Salvar Relatório de Varredura",
    )

    if arquivo_destino:
        try:
            with open(arquivo_destino, "w", encoding="utf-8") as f:
                f.write(conteudo_relatorio)
            messagebox.showinfo("Sucesso", "Relatório exportado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo:\n{e}")


root = ctk.CTk()
root.title("Python Port Scanner Visual v3.0")
root.geometry("550x700")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (550 / 2)
y = (screen_height / 2) - (700 / 2)
root.geometry(f"+{int(x)}+{int(y)}")

main_frame = ctk.CTkFrame(root, corner_radius=15)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

label_titulo = ctk.CTkLabel(main_frame, text="Port Scanner", font=("Roboto", 22, "bold"))
label_titulo.pack(pady=(20, 10))

input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
input_frame.pack(pady=10)

ctk.CTkLabel(input_frame, text="Endereço IP:", font=("Roboto", 12)).grid(
    row=0, column=0, sticky="w", padx=10, pady=5
)
entry_ip = ctk.CTkEntry(input_frame, width=200, placeholder_text="Ex: 127.0.0.1")
entry_ip.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
entry_ip.insert(0, "127.0.0.1")

ctk.CTkLabel(input_frame, text="Porta Inicial:", font=("Roboto", 12)).grid(
    row=1, column=0, sticky="w", padx=10, pady=5
)
entry_inicio = ctk.CTkEntry(input_frame, width=80)
entry_inicio.grid(row=1, column=1, sticky="w", padx=10, pady=5)
entry_inicio.insert(0, "1")

ctk.CTkLabel(input_frame, text="Porta Final:", font=("Roboto", 12)).grid(
    row=1, column=2, sticky="w", padx=10, pady=5
)
entry_fim = ctk.CTkEntry(input_frame, width=80)
entry_fim.grid(row=1, column=3, sticky="w", padx=10, pady=5)
entry_fim.insert(0, "1024")

btn_scan = ctk.CTkButton(
    main_frame,
    text="Iniciar Scan",
    font=("Roboto", 14, "bold"),
    height=40,
    corner_radius=20,
    command=iniciar_thread,
)
btn_scan.pack(pady=(15, 10))

progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
progress_frame.pack(fill="x", padx=30, pady=5)

progresso_bar = ctk.CTkProgressBar(progress_frame, width=380)
progresso_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
progresso_bar.set(0.0)

label_porcentagem = ctk.CTkLabel(progress_frame, text="0%", font=("Roboto", 12, "bold"), width=40)
label_porcentagem.pack(side="right")

label_resultados = ctk.CTkLabel(main_frame, text="Resultados do Scan:", font=("Roboto", 12))
label_resultados.pack(anchor="w", padx=25, pady=(10, 0))

text_saida = ctk.CTkTextbox(
    main_frame,
    width=480,
    height=250,
    font=("Consolas", 11),
    corner_radius=10,
    border_width=1,
    border_color="#333333",
)
text_saida.pack(padx=25, pady=5, fill="both", expand=True)

btn_exportar = ctk.CTkButton(
    main_frame,
    text="Salvar Relatório",
    font=("Roboto", 13),
    fg_color="#2c3e50",
    hover_color="#34495e",
    height=35,
    corner_radius=10,
    state="disabled",
    command=salvar_relatorio,
)
btn_exportar.pack(pady=(10, 20))

root.mainloop()
