import math
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
from tkinter.font import nametofont

# -------------------------------------------------------------------
# 1. FUNCIÓN DE AYUDA PARA SUPERÍNDICES
# -------------------------------------------------------------------
def to_superscript(n):
    n_str = str(n)
    superscript_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return "".join(superscript_map.get(digit, '') for digit in n_str)

# -------------------------------------------------------------------
# 2. CLASE POLYNOMIAL (Lógica sin cambios)
# -------------------------------------------------------------------
class Polynomial:
    def __init__(self, coeffs):
        self.coeffs = [float(c) for c in coeffs]
        self._normalize()
    def _normalize(self):
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0: self.coeffs.pop()
        if not self.coeffs: self.coeffs = [0]
    def degree(self):
        if self.coeffs == [0]: return -math.inf
        return len(self.coeffs) - 1
    def __str__(self):
        if self.coeffs == [0]: return "0"
        terms = []
        for power, coeff in reversed(list(enumerate(self.coeffs))):
            if coeff == 0: continue
            sign = " + " if coeff > 0 else " - "
            coeff = abs(coeff)
            coeff_str = f"{coeff:g}" if coeff != 1 or power == 0 else ""
            power_str = "x" if power == 1 else (f"x{to_superscript(power)}" if power > 1 else "")
            terms.append(f"{sign}{coeff_str}{power_str}")
        result = "".join(terms)
        return result[3:] if result.startswith(" + ") else ("-" + result[3:] if result.startswith(" - ") else "0")
    def __repr__(self): return f"Polynomial({self.coeffs})"
    def __eq__(self, other): return self.coeffs == other.coeffs
    def __add__(self, other):
        len1, len2 = len(self.coeffs), len(other.coeffs); new_len = max(len1, len2)
        c1 = self.coeffs + [0] * (new_len - len1); c2 = other.coeffs + [0] * (new_len - len2)
        return Polynomial([c1[i] + c2[i] for i in range(new_len)])
    def __sub__(self, other):
        len1, len2 = len(self.coeffs), len(other.coeffs); new_len = max(len1, len2)
        c1 = self.coeffs + [0] * (new_len - len1); c2 = other.coeffs + [0] * (new_len - len2)
        return Polynomial([c1[i] - c2[i] for i in range(new_len)])
    def __mul__(self, other):
        deg1, deg2 = self.degree(), other.degree()
        if deg1 == -math.inf or deg2 == -math.inf: return Polynomial([0])
        res_coeffs = [0] * (deg1 + deg2 + 1)
        for i, c1 in enumerate(self.coeffs):
            for j, c2 in enumerate(other.coeffs): res_coeffs[i + j] += c1 * c2
        return Polynomial(res_coeffs)
    def __divmod__(self, other):
        if other.coeffs == [0]: raise ZeroDivisionError("División por polinomio cero")
        num, den = list(self.coeffs), list(other.coeffs)
        deg_num, deg_den = len(num) - 1, len(den) - 1
        if deg_num < deg_den: return Polynomial([0]), Polynomial(num)
        q_coeffs = [0] * (deg_num - deg_den + 1)
        while deg_num >= deg_den and num != [0]:
            d = num[-1] / den[-1]; pos = deg_num - deg_den; q_coeffs[pos] = d
            for i, c_den in enumerate(den):
                idx = i + pos
                if idx < len(num): num[idx] -= d * c_den
            while len(num) > 1 and num[-1] == 0: num.pop()
            if not num: num = [0]
            deg_num = len(num) - 1
        return Polynomial(q_coeffs), Polynomial(num)
    def __truediv__(self, other): return self.__divmod__(other)[0]
    def __mod__(self, other): return self.__divmod__(other)[1]

# -------------------------------------------------------------------
# 3. LÓGICA DE LA INTERFAZ GRÁFICA (GUI)
# -------------------------------------------------------------------

class PolyApp:
    def __init__(self, root):
        self.root = root
        root.title("Calculadora de Polinomios")
        root.geometry("750x450") 
        root.minsize(600, 400)

        # --- Configuración de Fuente Global ---
        self.font_family = "Comfortaa"
        self.font_size = 11
        
        try:
            default_font = nametofont("TkDefaultFont")
            default_font.configure(family=self.font_family, size=self.font_size)
            text_font = nametofont("TkTextFont")
            text_font.configure(family=self.font_family, size=self.font_size)
            fixed_font = nametofont("TkFixedFont")
            fixed_font.configure(family=self.font_family, size=self.font_size)
            root.option_add("*Font", default_font)
        except Exception as e:
            print(f"Advertencia: No se pudo cargar la fuente '{self.font_family}'. Usando fuente por defecto. Error: {e}")
            self.font_family = "Helvetica" 

        # --- Definir fuentes específicas ---
        self.font_bold = (self.font_family, self.font_size, "bold")
        self.font_title = (self.font_family, self.font_size + 1, "bold")
        self.font_result = (self.font_family, self.font_size + 4, "bold") # Tamaño 15

        # --- Layout Principal (PanedWindow) ---
        main_pane = ttk.PanedWindow(root, orient=HORIZONTAL)
        main_pane.pack(fill=BOTH, expand=True)

        # --- Panel Izquierdo (Controles) ---
        control_frame = self.create_control_panel(main_pane)
        main_pane.add(control_frame, weight=1)

        # --- Panel Derecho (Resultados) ---
        output_frame = self.create_output_panel(main_pane)
        main_pane.add(output_frame, weight=2)

        # --- Configuración de Colores Neón para Salida ---
        self.color_op = self.root.style.colors.get('info')        
        self.color_error = self.root.style.colors.get('danger')   
        self.color_result_text = self.root.style.colors.get('warning') 
        self.color_result_bg = "#5e2e8f" 
        
        self.font_output_bold = (self.font_family, self.font_size, "bold")
        
        self.output_text.tag_configure("op", foreground=self.color_op, font=self.font_output_bold)
        self.output_text.tag_configure("error", foreground=self.color_error, font=self.font_output_bold)
        self.output_text.tag_configure("result_text", foreground=self.color_result_text, font=self.font_result)
        self.output_text.tag_configure("result_bg", background=self.color_result_bg, lmargin1=10, lmargin2=10)


    def create_control_panel(self, parent):
        """Crea el panel lateral izquierdo con entradas y botones."""
        control_frame = ttk.Frame(parent, padding=15)
        
        # --- Configuración de la rejilla (grid) del panel ---
        # Volvemos a un layout simple de 1 columna
        control_frame.grid_rowconfigure(0, weight=0) # Entradas
        control_frame.grid_rowconfigure(1, weight=0) # Botones
        control_frame.grid_rowconfigure(2, weight=1) # Espacio para empujar
        control_frame.grid_columnconfigure(0, weight=1) # 1 Columna

        # --- Grupo de Entradas ---
        input_group = ttk.LabelFrame(control_frame, text="Polinomios", padding=10) 
        # Ocupa la columna 0 y se estira (ew)
        input_group.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_group.columnconfigure(1, weight=1)

        ttk.Label(input_group, text="P1(x)", font=self.font_bold).grid(row=0, column=0, padx=5, pady=8)
        self.p1_entry = ttk.Entry(input_group)
        self.p1_entry.grid(row=0, column=1, sticky=EW)
        
        ttk.Label(input_group, text="P2(x)", font=self.font_bold).grid(row=1, column=0, padx=5, pady=8)
        self.p2_entry = ttk.Entry(input_group)
        self.p2_entry.grid(row=1, column=1, sticky=EW)
        
        info_label = ttk.Label(input_group, text="Ej: -5 2 3 (para 3x² + 2x - 5)", bootstyle=INFO, wraplength=200, justify=LEFT)
        info_label.grid(row=2, column=0, columnspan=2, pady=(10,0))

        # --- Grupo de Botones ---
        button_group = ttk.LabelFrame(control_frame, text="Operaciones ⚙", padding=10)
        # Ocupa la columna 0 y se estira (ew)
        button_group.grid(row=1, column=0, sticky="ew") 
        
        # Hacemos que las columnas INTERNAS del grupo de botones tengan el mismo ancho
        button_group.columnconfigure(0, weight=1)
        button_group.columnconfigure(1, weight=1)
        
        self.add_btn = ttk.Button(button_group, text="Sumar +", command=lambda: self.calculate('add'), bootstyle=INFO)
        self.sub_btn = ttk.Button(button_group, text="Restar -", command=lambda: self.calculate('sub'), bootstyle=INFO)
        self.mul_btn = ttk.Button(button_group, text="Multiplicar X", command=lambda: self.calculate('mul'), bootstyle=INFO)
        self.div_btn = ttk.Button(button_group, text="Dividir ÷", command=lambda: self.calculate('div'), bootstyle=INFO)
        self.clr_btn = ttk.Button(button_group, text="Limpiar Resultados", command=self.clear_output, bootstyle=WARNING)

        # --- COLOCACIÓN CORRECTA ---
        # Sin sticky, los botones se centrarán en su celda (que tiene weight=1)
        # Añadimos padding para que no se peguen entre sí
        self.add_btn.grid(row=0, column=0, sticky="", padx=5, pady=5) 
        self.sub_btn.grid(row=0, column=1, sticky="", padx=5, pady=5)
        self.mul_btn.grid(row=1, column=0, sticky="", padx=5, pady=5)
        self.div_btn.grid(row=1, column=1, sticky="", padx=5, pady=5)
        
        # El botón naranja SÍ usa sticky="ew" para expandirse
        self.clr_btn.grid(row=2, column=0, columnspan=2, sticky="ew", padx=3, pady=(8,3))
        
        return control_frame

    def create_output_panel(self, parent):
        """Crea el panel lateral derecho con el área de texto."""
        output_frame = ttk.Frame(parent, padding=(5, 15, 15, 15))
        output_frame.pack(fill=BOTH, expand=True)

        ttk.Label(output_frame, text="Resultados", font=self.font_title).pack(anchor=NW)

        st_frame = ttk.Frame(output_frame, padding=2, bootstyle=SECONDARY)
        st_frame.pack(fill=BOTH, expand=True, pady=(5,0))
        
        self.output_text = ScrolledText(st_frame, height=10, width=50, 
                                        font=(self.font_family, self.font_size), 
                                        wrap=WORD, relief=FLAT, bd=0)
        self.output_text.pack(fill=BOTH, expand=True)
        self.output_text.config(state=DISABLED)
        
        return output_frame

    def write_output(self, text, style_tag=None):
        """Escribe en el área de resultado usando tags de estilo."""
        self.output_text.config(state=NORMAL)
        
        if style_tag == "result_text":
            self.output_text.insert(END, text + "\n", ("result_text", "result_bg"))
        elif style_tag:
            self.output_text.insert(END, text + "\n", style_tag)
        else:
            self.output_text.insert(END, text + "\F\n")
            
        if style_tag == "result_text":
            self.output_text.insert(END, "\n")
            
        self.output_text.config(state=DISABLED)
        self.output_text.see(END) 

    def clear_output(self):
        self.output_text.config(state=NORMAL)
        self.output_text.delete(1.0, END)
        self.output_text.config(state=DISABLED)

    def parse_polynomial(self, entry_widget):
        raw_text = entry_widget.get().strip()
        if not raw_text: raise ValueError("El campo está vacío.")
        coeffs = raw_text.split()
        return Polynomial(coeffs)

    def calculate(self, operation):
        """Función principal"""
        try:
            P1 = self.parse_polynomial(self.p1_entry)
            P2 = self.parse_polynomial(self.p2_entry)
            p1_str, p2_str = f"({P1})", f"({P2})"

            if operation == 'add':
                self.write_output(f"Suma + {p1_str} + {p2_str}", "op")
                self.write_output(f"= {P1 + P2}", "result_text") 
            elif operation == 'sub':
                self.write_output(f"Resta - {p1_str} - {p2_str}", "op")
                self.write_output(f"= {P1 - P2}", "result_text")
            elif operation == 'mul':
                self.write_output(f"Multiplicación X {p1_str} * {p2_str}", "op")
                self.write_output(f"= {P1 * P2}", "result_text")
            elif operation == 'div':
                q, r = divmod(P1, P2)
                self.write_output(f"División ÷ {p1_str} / {p2_str}", "op")
                self.write_output(f"Cociente:  {q}", "result_text") 
                self.write_output(f"Resto:     {r}", "result_text")

        except ZeroDivisionError:
            self.write_output("Error: No se puede dividir por el polinomio cero.", "error")
        except ValueError as e:
            self.write_output(f"Error de entrada: {e}", "error")
        except Exception as e:
            self.write_output(f"Error inesperado: {e}", "error")

# -------------------------------------------------------------------
# 4. EJECUCIÓN PRINCIPAL
# -------------------------------------------------------------------
if __name__ == "__main__":
    app = ttk.Window(themename="cyborg")
    PolyApp(app)
    app.mainloop()