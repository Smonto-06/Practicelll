import re
import tkinter as tk
from tkinter import messagebox

class AnalizadorSAN:
    def __init__(self):
        # Compilar regex según BNF SAN
        self.enroque = re.compile(r'^(O-O(?:-O)?)$')
        self.mov_pieza = re.compile(r'^[KQRBN](?:(?:[a-h][1-8])|[a-h]|[1-8])?x?[a-h][1-8](?:=[KQRBN])?[+#]?$')
        self.mov_peon_avance = re.compile(r'^[a-h][1-8](?:=[KQRBN])?[+#]?$')
        self.mov_peon_captura = re.compile(r'^[a-h]x[a-h][1-8](?:=[KQRBN])?[+#]?$')

    def validar_movimiento(self, mov):
        if self.enroque.match(mov): return True, None
        if self.mov_pieza.match(mov): return True, None
        if self.mov_peon_avance.match(mov): return True, None
        if self.mov_peon_captura.match(mov): return True, None
        return False, 'No cumple con SAN según la BNF'

    def parsear_partida(self, texto):
        # Normalizar el texto
        texto_norm = ' '.join(texto.split())
        patron = re.compile(r'(\d+)\.\s*([^\s]+)(?:\s+([^\s]+))?')
        turnos = patron.findall(texto_norm)
        # Reconstruir para comparar
        recolectado = ' '.join(
            f"{n}. {b}{(' '+k) if k else ''}" for n,b,k in turnos
        )
        if recolectado != texto_norm:
            return None, 'Formato de partida inválido o texto extra'
        return turnos, None

class Nodo:
    def __init__(self, etiqueta):
        self.etiqueta = etiqueta
        self.x = 0
        self.y = 0

class Aplicacion:
    def __init__(self, root):
        self.root = root
        root.title('Parser de Partida de Ajedrez')
        self.parser = AnalizadorSAN()

        # Entrada SAN
        self.texto = tk.Text(root, height=6, wrap='word')
        self.texto.pack(fill='x', padx=10, pady=5)

        tk.Button(root, text='Validar y Mostrar Árbol', command=self.procesar).pack(pady=5)

        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(frame, bg='white')
        self.canvas.pack(side='left', fill='both', expand=True)
        tk.Scrollbar(frame, orient='vertical', command=self.canvas.yview).pack(side='right', fill='y')
        tk.Scrollbar(frame, orient='horizontal', command=self.canvas.xview).pack(side='bottom', fill='x')
        self.canvas.config(xscrollcommand=lambda *a: None, yscrollcommand=lambda *a: None)

        tk.Label(root, text='Óvalos blancos=Blancas · Óvalos grises=Negras').pack(pady=2)

    def procesar(self):
        self.canvas.delete('all')
        san = self.texto.get('1.0', tk.END)
        turnos, error = self.parser.parsear_partida(san)
        if error:
            messagebox.showerror('Error', error)
            return

        # Generar nodos en comb: blanco spine y negros hermanos
        spine = []
        blacks = []
        for num, bl, neg in turnos:
            spine.append(Nodo(f'{num}. {bl}'))
            blacks.append(Nodo(f'{num}... {neg}') if neg else None)

        # Layout
        c_w = self.canvas.winfo_width() or self.canvas.winfo_reqwidth()
        c_h = self.canvas.winfo_height() or self.canvas.winfo_reqheight()
        root_x = c_w/2
        root_y = 20
        n = len(spine)
        dx = root_x/(n+1)
        dy = 80

        # Posiciones
        # raíz
        self.canvas.origin = (root_x, root_y)
        prev_x, prev_y = root_x, root_y
        for i, node in enumerate(spine, start=1):
            x_w = root_x - dx*i
            y = root_y + dy*i
            node.x, node.y = x_w, y
            # negro
            if blacks[i-1]:
                x_b = root_x + dx*i
                blacks[i-1].x, blacks[i-1].y = x_b, y

        # Dibujar
        # raíz
        t = self.canvas.create_text(root_x, root_y, text='Partida', font=('Arial',12,'bold'))
        x0,y0,x1,y1 = self.canvas.bbox(t)
        self.canvas.create_oval(x0-5,y0-5,x1+5,y1+5,fill='white',outline='black')
        self.canvas.tag_raise(t)
        # aristas y nodos
        px, py = root_x, root_y
        for i, node in enumerate(spine):
            # blanca
            self.canvas.create_line(px, py+10, node.x, node.y-10)
            t = self.canvas.create_text(node.x, node.y, text=node.etiqueta, font=('Arial',10,'bold'),fill='black')
            x0,y0,x1,y1 = self.canvas.bbox(t)
            o = self.canvas.create_oval(x0-4,y0-4,x1+4,y1+4,fill='white',outline='black')
            self.canvas.tag_raise(t)
            # negra
            nb = blacks[i]
            if nb:
                self.canvas.create_line(px, py+10, nb.x, nb.y-10)
                t2 = self.canvas.create_text(nb.x, nb.y, text=nb.etiqueta, font=('Arial',10,'bold'),fill='white')
                x0,y0,x1,y1 = self.canvas.bbox(t2)
                o2 = self.canvas.create_oval(x0-4,y0-4,x1+4,y1+4,fill='gray20',outline='black')
                self.canvas.tag_raise(t2)
            # next spine parent
            px, py = node.x, node.y

        # Ajustar scrollregion
        self.canvas.config(scrollregion=self.canvas.bbox('all'))

if __name__ == '__main__':
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()

