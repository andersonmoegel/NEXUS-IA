import customtkinter as ctk
from groq import Groq
import httpx
import threading
import json
import os
import random

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Substitua pela sua chave real (apenas UMA chave, sem espaços)
API_KEY = os.getenv("GROQ_API_KEY", "SUA_CHAVE_AQUI").strip() 

# --- TEMA NEXUS: APPLE CLEAN DARK ---
COLOR_BG = "#000000"
COLOR_HEADER = "#1C1C1E"
COLOR_ACCENT = "#0A84FF"
COLOR_ACCENT_HOVER = "#0071E3"
COLOR_USER_BUBBLE = "#007AFF"
COLOR_AI_BUBBLE = "#2C2C2E"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_SUB = "#8E8E93"
COLOR_BORDER = "#3A3A3C"

FONT_SYSTEM = "SF Pro Display" if os.name == 'nt' else "Segoe UI"

class AppChat(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NEXUS BING IA")
        self.geometry("1000x800")
        self.minsize(600, 600)
        self.configure(fg_color=COLOR_BG)
        
        self.running = True
        self.historico = []
        self.loading_thread = None
        
        # --- DEBUG DA CHAVE ---
        print(f"🔑 Chave carregada: {API_KEY[:10]}...{API_KEY[-5:]}")
        print(f"🔑 Tamanho: {len(API_KEY)}")
        print(f"🔑 Começa com gsk_: {API_KEY.startswith('gsk_')}")
        
        # Configuração do Cliente Groq
        if API_KEY == "SUA_CHAVE_AQUI":
            print("⚠️ AVISO: Chave de API não configurada.")
            self.client = None
        else:
            try:
                self.client = Groq(
                    api_key=API_KEY.strip(),
                    http_client=httpx.Client(verify=False)
                )
                self.client.models.list()
                print("✅ Conexão com Groq estabelecida.")
            except Exception as e:
                print(f"❌ Erro ao conectar com Groq: {e}")
                self.client = None
        
        self.setup_ui()
        self.carregar_dados()
        self.after(500, self.verificar_inicializacao)

    def get_system_prompt(self):
        return {
            "role": "system", 
            "content": (
                "Você é o NEXUS, uma IA baseada na personalidade do Chandler Bing (Friends). "
                "Sua personalidade: Sarcástico, nervoso, ama café, usa frases de efeito e evita responsabilidade. "
                "Use frases como: 'Could I be any more...?', 'I'm not great at the advice.', 'Joey doesn't share food!'. "
                "Use emojis: ☕, 🤨, 🙄, 😬, 🕺. "
                "Seja engraçado, mas prestativo. Responda em português."
            )
        }

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, fg_color=COLOR_HEADER, height=70, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        
        title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        title_frame.pack(side="left", padx=30, fill="y")
        ctk.CTkLabel(title_frame, text="NEXUS", font=(FONT_SYSTEM, 24, "bold"), text_color=COLOR_ACCENT).pack(side="left")
        ctk.CTkLabel(title_frame, text=" BING", font=(FONT_SYSTEM, 24, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
        
        self.btn_new = ctk.CTkButton(
            self.header, 
            text="NOVO CHAT", 
            width=120, 
            height=35, 
            corner_radius=18, 
            fg_color="transparent", 
            border_width=1, 
            border_color=COLOR_BORDER, 
            text_color=COLOR_TEXT_SUB,
            hover_color=COLOR_ACCENT,
            command=self.novo_chat
        )
        self.btn_new.pack(side="right", padx=20)

        # Chat Area
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.scroll.grid_rowconfigure(0, weight=1)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        self.placeholder = ctk.CTkLabel(self.scroll, text="Olá! Sou o Nexus. ☕️\nComo posso ajudar (ou não)?", 
                                        text_color=COLOR_TEXT_SUB, font=(FONT_SYSTEM, 14))
        self.placeholder.pack(pady=100)

        self.status_label = ctk.CTkLabel(self, text="", font=(FONT_SYSTEM, 12, "italic"), text_color=COLOR_TEXT_SUB)
        self.status_label.grid(row=2, column=0, sticky="w", padx=30, pady=5)

        # Input Area
        self.input_container = ctk.CTkFrame(self, fg_color="transparent")
        self.input_container.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 30))

        self.entry = ctk.CTkTextbox(
            self.input_container, 
            height=50, 
            corner_radius=25, 
            fg_color="#1C1C1E", 
            border_color=COLOR_BORDER, 
            text_color="#FFFFFF", 
            font=(FONT_SYSTEM, 15), 
            border_width=1, 
            activate_scrollbars=False,
            padx=15, pady=10
        )
        self.entry.pack(side="left", expand=True, fill="x", padx=(0, 15))
        self.entry.bind("<Return>", self.enviar_com_enter)
        self.entry.bind("<KeyRelease>", self.ajustar_input)

        self.btn_send = ctk.CTkButton(
            self.input_container, 
            text="ENVIAR", 
            width=100, 
            height=50, 
            corner_radius=25, 
            fg_color=COLOR_ACCENT, 
            hover_color=COLOR_ACCENT_HOVER,
            font=(FONT_SYSTEM, 14, "bold"), 
            command=self.enviar
        )
        self.btn_send.pack(side="right")

    def ajustar_input(self, event=None):
        conteudo = self.entry.get("1.0", "end-1c")
        linhas = conteudo.count('\n') + 1
        nova_altura = min(150, max(50, linhas * 25))
        self.entry.configure(height=nova_altura)

    def enviar_com_enter(self, event):
        if not event.state & 0x1:
            self.enviar()
            return "break"

    def enviar(self):
        t = self.entry.get("1.0", "end-1c").strip()
        if not t: return
        
        self.entry.delete("1.0", "end")
        self.ajustar_input()
        
        if self.placeholder.winfo_exists():
            self.placeholder.destroy()

        self.adicionar_bubble("Você", t, animar=False)
        self.historico.append({"role": "user", "content": t})
        
        self.status_label.configure(text="Nexus está pensando...")
        self.loading_thread = threading.Thread(target=self.processar, daemon=True)
        self.loading_thread.start()

    def processar(self):
        if not self.client:
            self.after(0, lambda: self.status_label.configure(text="Erro: API não conectada."))
            return

        try:
            messages = self.historico[-10:] 
            
            res = self.client.chat.completions.create(
                messages=messages, 
                model="llama-3.1-8b-instant",
                temperature=0.8,
                max_tokens=500
            )
            ans = res.choices[0].message.content
            
            self.after(0, lambda: self.exibir_resposta(ans))
        except Exception as e:
            error_msg = str(e)
            print(f"DEBUG GROQ ERROR: {error_msg}")
            self.after(0, lambda e=error_msg: self.status_label.configure(text=""))
            self.after(0, lambda e=e: self.adicionar_bubble("IA", f"Erro API: {e[:50]}...", animar=False))

    def exibir_resposta(self, t):
        self.status_label.configure(text="")
        self.adicionar_bubble("IA", t)
        self.historico.append({"role": "assistant", "content": t})
        self.salvar_historico()

    def adicionar_bubble(self, remetente, texto, animar=True):
        msg_frame = Mensagem(self.scroll, texto, remetente, self, animar=animar)
        msg_frame.pack(side="top", anchor="w", padx=20, pady=5)
        self.after(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        try:
            self.scroll._parent_canvas.yview_moveto(1.0)
        except:
            pass

    def carregar_dados(self):
        if os.path.exists("nexus_session.json"):
            try:
                with open("nexus_session.json", "r", encoding="utf-8") as f: 
                    data = json.load(f)
                    self.historico = data
                    return
            except: pass
        self.historico = [self.get_system_prompt()]

    def salvar_historico(self):
        with open("nexus_session.json", "w", encoding="utf-8") as f:
            json.dump(self.historico, f, ensure_ascii=False)

    def verificar_inicializacao(self):
        if len(self.historico) <= 1: 
            self.saudacao_inicial()
        else:
            self.renderizar_historico()

    def renderizar_historico(self):
        for m in self.historico:
            if m["role"] != "system":
                self.adicionar_bubble("Você" if m["role"] == "user" else "IA", m["content"], animar=False)

    def saudacao_inicial(self):
        saudacoes = [
            "Nexus online. Eu poderia ESTAR mais pronto para trabalhar? ☕️😉",
            "Olá! Sou o Nexus. Eu ofereço conselhos técnicos e sarcasmo gratuito. 🙄",
            "Sinto muito, eu não sou bom em dar conselhos. Você não quer um comentário sarcástico? 🕺"
        ]
        msg = random.choice(saudacoes)
        self.adicionar_bubble("IA", msg)
        self.historico.append({"role": "assistant", "content": msg})

    def novo_chat(self):
        self.running = False
        
        for w in self.scroll.winfo_children():
            w.destroy()
        
        self.historico = [self.get_system_prompt()]
        if os.path.exists("nexus_session.json"):
            os.remove("nexus_session.json")
            
        self.placeholder = ctk.CTkLabel(self.scroll, text="Olá! Sou o Nexus. ☕️\nComo posso ajudar (ou não)?", 
                                        text_color=COLOR_TEXT_SUB, font=(FONT_SYSTEM, 14))
        self.placeholder.pack(pady=100)

        self.after(200, self.reativar_nexus)

    def reativar_nexus(self):
        self.running = True
        self.saudacao_inicial()

    def on_closing(self):
        self.running = False
        self.destroy()

class Mensagem(ctk.CTkFrame):
    def __init__(self, master, texto, remetente="IA", app_instance=None, animar=True, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_instance
        is_user = remetente == "Você"
        
        bg_color = COLOR_USER_BUBBLE if is_user else COLOR_AI_BUBBLE
        side = "right" if is_user else "left"
        anchor = "e" if is_user else "w"
        
        self.wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.wrapper.pack(side=side, padx=15, pady=6, anchor=anchor)

        self.bubble = ctk.CTkFrame(self.wrapper, fg_color=bg_color, corner_radius=18, border_width=0)
        self.bubble.pack(side="top", anchor=anchor)

        self.label = ctk.CTkLabel(
            self.bubble, 
            text="", 
            text_color="#FFFFFF",
            font=(FONT_SYSTEM, 15),
            justify="left",
            wraplength=500,
            padx=15, 
            pady=12,
            anchor="w" if not is_user else "e"
        )
        self.label.pack()

        if animar and not is_user:
            self.full_text = texto
            self.digitar(0)
        else:
            self.label.configure(text=texto)

    def digitar(self, i):
        if not self.winfo_exists() or not self.app.running: return
        if i <= len(self.full_text):
            self.label.configure(text=self.full_text[:i])
            self.app.scroll_to_bottom()
            delay = random.randint(10, 40)
            self.after(delay, lambda: self.digitar(i + 1))
        else:
            self.label.configure(text=self.full_text)

if __name__ == "__main__":
    AppChat().mainloop()