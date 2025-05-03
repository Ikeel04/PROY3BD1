import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psycopg2
from datetime import datetime
import csv
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry

class ReportesEmpresaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reportes - Empresa")
        self.root.geometry("1200x800")
        
        # Conexión a la base de datos
        self.conn = psycopg2.connect(
            dbname="negroshima",
            user="postgres",
            password="admin",
            host="localhost"
        )
        self.cursor = self.conn.cursor()
        
        self.crear_interfaz()
    #Estructura copiada del otro archivo
    def crear_interfaz(self):
       
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.reportes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reportes_frame, text="Reportes por fecha")
        self.pest_rep()

        self.graficos_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graficos_frame, text="Graficas")
        self.grafica()

        self.consultas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.consultas_frame, text=" SQL")
        self.consultas()
    
    def pest_rep(self):

        filtros_frame = ttk.LabelFrame(self.reportes_frame, text="Filtros", padding="10")
        filtros_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filtros_frame, text="Fecha inicial:").grid(row=0, column=0, padx=5, pady=5)
        self.fecha_inicio = DateEntry(
            filtros_frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.fecha_inicio.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filtros_frame, text="Fecha final:").grid(row=0, column=2, padx=5, pady=5)
        self.fecha_fin = DateEntry(
            filtros_frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.fecha_fin.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filtros_frame, text="Estado reserva:").grid(row=0, column=4, padx=5, pady=5)
        self.estado_reserva = ttk.Combobox(
            filtros_frame, 
            values=["Todos", "pendiente", "confirmada", "cancelada", "completada"],
            state="readonly"
        )
        self.estado_reserva.set("Todos")
        self.estado_reserva.grid(row=0, column=5, padx=5, pady=5)
        

        ttk.Button(
            filtros_frame, 
            text="Generar Reporte", 
            command=self.gen_rep
        ).grid(row=0, column=6, padx=10, pady=5)

        self.reportes_tree = ttk.Treeview(
            self.reportes_frame,
            columns=("id", "cancha", "usuario", "fecha", "hora_inicio", "hora_fin", "duracion", "estado", "total"),
            show="headings"
        )

        columnas = [
            ("id", "ID", 50),
            ("cancha", "Cancha", 150),
            ("usuario", "Usuario", 150),
            ("fecha", "Fecha", 100),
            ("hora_inicio", "Hora Inicio", 80),
            ("hora_fin", "Hora Fin", 80),
            ("duracion", "Duración", 80),
            ("estado", "Estado", 100),
            ("total", "Total", 100)
        ]
        
        for col, text, width in columnas:
            self.reportes_tree.heading(col, text=text)
            self.reportes_tree.column(col, width=width)
        

        scrollbar = ttk.Scrollbar(self.reportes_frame, orient="vertical", command=self.reportes_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.reportes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.reportes_tree.pack(fill=tk.BOTH, expand=True)

        export_frame = ttk.Frame(self.reportes_frame)
        export_frame.pack(side="right", padx=5, pady=5)
        
        # Botón de exportar a CSV
        ttk.Button(
            export_frame, 
            text="Exportar a CSV", 
            command=self.exportar_a_csv
        ).pack(side="left", padx=5)
        
        # Botón de exportar a PDF
        ttk.Button(
            export_frame, 
            text="Exportar a PDF", 
            command=self.exportar_a_pdf
        ).pack(side="left", padx=5)

    def grafica(self):

        opciones_frame = ttk.LabelFrame(self.graficos_frame, text="Opciones de Gráfico", padding="10")
        opciones_frame.pack(fill=tk.X, pady=5)

        ttk.Label(opciones_frame, text="Tipo de gráfico:").grid(row=0, column=0, padx=5, pady=5)
        self.tipo_grafico = ttk.Combobox(
            opciones_frame,
            values=["Reservas por día", "Ingresos por cancha", "Uso de servicios", "Estado de reservas"],
            state="readonly"
        )
        self.tipo_grafico.set("Reservas por día")
        self.tipo_grafico.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(opciones_frame, text="Fecha inicial:").grid(row=0, column=2, padx=5, pady=5)
        self.grafico_fecha_inicio = DateEntry(
            opciones_frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.grafico_fecha_inicio.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(opciones_frame, text="Fecha final:").grid(row=0, column=4, padx=5, pady=5)
        self.grafico_fecha_fin = DateEntry(
            opciones_frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.grafico_fecha_fin.grid(row=0, column=5, padx=5, pady=5)
        
        # Botón para generar gráfico
        ttk.Button(
            opciones_frame, 
            text="Gráfica", 
            command=self.generar_grafico
        ).grid(row=0, column=6, padx=10, pady=5)

        self.grafico_frame = ttk.Frame(self.graficos_frame)
        self.grafico_frame.pack(fill=tk.BOTH, expand=True)
    
    def consultas(self):

        consulta_frame = ttk.LabelFrame(self.consultas_frame, text="SQL", padding="10")
        consulta_frame.pack(fill=tk.X, pady=5)

        self.consulta_text = tk.Text(consulta_frame, height=5, width=80)
        self.consulta_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(consulta_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame, 
            text="Consultar", 
            command=self.ejecutar_consulta
        ).pack(side="left", padx=5, pady=5)
        
        ttk.Button(
            btn_frame, 
            text="Limpiar", 
            command=self.limpiar_consulta
        ).pack(side="left", padx=5, pady=5)
        
        # Resultados
        self.consulta_tree = ttk.Treeview(self.consultas_frame)
        

        scrollbar = ttk.Scrollbar(self.consultas_frame, orient="vertical", command=self.consulta_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.consulta_tree.configure(yscrollcommand=scrollbar.set)
        
        self.consulta_tree.pack(fill=tk.BOTH, expand=True)
    
    def gen_rep(self):

        fecha_inicio = self.fecha_inicio.get_date()
        fecha_fin = self.fecha_fin.get_date()
        estado = self.estado_reserva.get()

        query = """
        SELECT 
            r.id, 
            c.nombre AS cancha, 
            u.nombre AS usuario, 
            r.fecha, 
            r.hora_inicio, 
            r.hora_fin, 
            r.duracion, 
            r.estado
        FROM reserva r
        JOIN cancha c ON r.id_cancha = c.id
        JOIN usuario u ON r.id_usuario = u.id
        WHERE r.fecha BETWEEN %s AND %s
        """
        
        params = [fecha_inicio, fecha_fin]
        
        if estado != "Todos":
            query += " AND r.estado = %s"
            params.append(estado)
        
        query += " ORDER BY r.fecha, r.hora_inicio"
        
        try:
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            

            for item in self.reportes_tree.get_children():
                self.reportes_tree.delete(item)

            for row in resultados:
                self.reportes_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_grafico(self):
        tipo = self.tipo_grafico.get()
        fecha_inicio = self.grafico_fecha_inicio.get_date()
        fecha_fin = self.grafico_fecha_fin.get_date()
        
        try:

            for widget in self.grafico_frame.winfo_children():
                widget.destroy()
            
            fig = plt.Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            if tipo == "Reservas por día":
                query = """
                SELECT fecha, COUNT(*) 
                FROM reserva 
                WHERE fecha BETWEEN %s AND %s
                GROUP BY fecha 
                ORDER BY fecha
                """
                self.cursor.execute(query, (fecha_inicio, fecha_fin))
                datos = self.cursor.fetchall()
                
                fechas = [d[0] for d in datos]
                cantidades = [d[1] for d in datos]
                
                ax.bar(fechas, cantidades)
                ax.set_title("Reservas por día")
                ax.set_xlabel("Fecha")
                ax.set_ylabel("Número de reservas")
                fig.autofmt_xdate()
                
            elif tipo == "Ingresos por cancha":
                query = """
                SELECT c.nombre, SUM(p.total) 
                FROM reserva r
                JOIN cancha c ON r.id_cancha = c.id
                JOIN pago p ON p.id_reserva = r.id
                WHERE r.fecha BETWEEN %s AND %s
                GROUP BY c.nombre
                ORDER BY SUM(p.total) DESC
                """
                self.cursor.execute(query, (fecha_inicio, fecha_fin))
                datos = self.cursor.fetchall()
                
                canchas = [d[0] for d in datos]
                ingresos = [float(d[1]) for d in datos]
                
                ax.bar(canchas, ingresos)
                ax.set_title("Ingresos por cancha")
                ax.set_xlabel("Cancha")
                ax.set_ylabel("Ingresos ($)")
                fig.autofmt_xdate()
                
            elif tipo == "Uso de servicios":
                query = """
                SELECT sa.descripcion, COUNT(rs.id_servicio)
                FROM reserva_servicio rs
                JOIN servicio_adicional sa ON rs.id_servicio = sa.id
                JOIN reserva r ON rs.id_reserva = r.id
                WHERE r.fecha BETWEEN %s AND %s
                GROUP BY sa.descripcion
                ORDER BY COUNT(rs.id_servicio) DESC
                """
                self.cursor.execute(query, (fecha_inicio, fecha_fin))
                datos = self.cursor.fetchall()
                
                servicios = [d[0] for d in datos]
                usos = [d[1] for d in datos]
                
                ax.pie(usos, labels=servicios, autopct='%1.1f%%')
                ax.set_title("Uso de servicios adicionales")
                
            elif tipo == "Estado de reservas":
                query = """
                SELECT estado, COUNT(*) 
                FROM reserva 
                WHERE fecha BETWEEN %s AND %s
                GROUP BY estado
                """
                self.cursor.execute(query, (fecha_inicio, fecha_fin))
                datos = self.cursor.fetchall()
                
                estados = [d[0] for d in datos]
                cantidades = [d[1] for d in datos]
                
                ax.pie(cantidades, labels=estados, autopct='%1.1f%%')
                ax.set_title("Distribución por estado de reservas")
            

            canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfico: {str(e)}")
    
    def ejecutar_consulta(self):
        consulta = self.consulta_text.get("1.0", tk.END).strip()
        
        if not consulta:
            messagebox.showwarning("Advertencia", "Por favor ingrese una consulta SQL")
            return
        
        try:
            self.cursor.execute(consulta)

            for item in self.consulta_tree.get_children():
                self.consulta_tree.delete(item)

            columnas = [desc[0] for desc in self.cursor.description]
            self.consulta_tree["columns"] = columnas
  
            for col in columnas:
                self.consulta_tree.heading(col, text=col)
                self.consulta_tree.column(col, width=100)
      
            for row in self.cursor.fetchall():
                self.consulta_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar consulta: {str(e)}")
    
    def limpiar_consulta(self):
        self.consulta_text.delete("1.0", tk.END)
        for item in self.consulta_tree.get_children():
            self.consulta_tree.delete(item)
    
    def exportar_a_csv(self):
  
            items = self.reportes_tree.get_children()
            if not items:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            # Pedir al usuario dónde guardar el archivo
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                title="Guardar como CSV"
            )
            
            if not filepath:  #por si ya no se quiere exportar
                return
            
            try:
                with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    headers = [self.reportes_tree.heading(col)['text'] for col in self.reportes_tree['columns']]
                    writer.writerow(headers)
                    

                    for item in items:
                        row = self.reportes_tree.item(item)['values']
                        writer.writerow(row)
                
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar a CSV: {str(e)}")
        
    def exportar_a_pdf(self):

            items = self.reportes_tree.get_children()
            if not items:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            # Pedir al usuario dónde guardar el archivo
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
                title="Guardar como PDF"
            )
            
            if not filepath:
                return
            
            try:
                # Crear PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                
                # Título del reporte
                pdf.cell(200, 10, txt="Reporte de Reservas", ln=1, align='C')
                
                # Fechas del reporte
                fecha_inicio = self.fecha_inicio.get_date().strftime("%d/%m/%Y")
                fecha_fin = self.fecha_fin.get_date().strftime("%d/%m/%Y")
                pdf.cell(200, 10, txt=f"Desde: {fecha_inicio} - Hasta: {fecha_fin}", ln=1, align='C')
                
                # Estado filtrado
                estado = self.estado_reserva.get()
                if estado != "Todos":
                    pdf.cell(200, 10, txt=f"Estado: {estado.capitalize()}", ln=1, align='C')
                
                pdf.ln(10) 
                
                # Encabezados de la tabla
                headers = [self.reportes_tree.heading(col)['text'] for col in self.reportes_tree['columns']]
                col_widths = [30, 40, 40, 25, 25, 25, 25, 30, 25] 
                
                # Configurar fuente para la tabla
                pdf.set_font("Arial", size=10)
                
              
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, txt=header, border=1)
                pdf.ln()
                

                for item in items:
                    row = self.reportes_tree.item(item)['values']
                    for i, value in enumerate(row):
                        pdf.cell(col_widths[i], 10, txt=str(value), border=1)
                    pdf.ln()

                pdf.output(filepath)
                messagebox.showinfo("Éxito", f"Reporte generado correctamente en:\n{filepath}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el PDF: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportesEmpresaApp(root)
    root.mainloop()