import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import psycopg2
from datetime import datetime
import csv
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MergedReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Integrado de Reportes")
        self.root.geometry("1200x800")

        # Conexión a la base de datos
        self.conn = psycopg2.connect(
            dbname="negroshima",
            user="postgres",
            password="0512",
            host="localhost",
            options='-c client_encoding=UTF8'
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestañas combinadas
        self.crear_reporte_por_fecha()
        self.crear_pestaña_graficas()
        self.crear_pestaña_sql()
        self.crear_reporte_ingresos()
        self.crear_reporte_servicios()
        self.crear_reporte_por_usuario()
        self.crear_reporte_duracion()
        self.crear_reporte_comparativo_mensual()

    # Helper genérico para pestañas con filtros + Treeview
    def crear_pestana_base(self, titulo, columnas, anchuras):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=titulo)

        filtros = ttk.LabelFrame(tab, text="Filtros", padding=8)
        filtros.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        resultado = ttk.LabelFrame(tab, text="Resultado", padding=8)
        resultado.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree = ttk.Treeview(resultado, columns=columnas, show="headings")
        for col, ancho in zip(columnas, anchuras):
            tree.heading(col, text=col.replace("_"," ").title())
            tree.column(col, width=ancho)
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        sb = ttk.Scrollbar(resultado, command=tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=sb.set)

        return filtros, tree

    # 1. Reporte por fecha + export CSV/PDF
    def crear_reporte_por_fecha(self):
        filtros, tree = self.crear_pestana_base(
            "Reportes por Fecha",
            ["id","cancha","usuario","fecha","hora_inicio","hora_fin","duracion","estado","total"],
            [50,150,150,100,80,80,80,100,100]
        )
        # Campos de filtro
        ttk.Label(filtros, text="Fecha inicial:").grid(row=0, column=0, padx=5, pady=5)
        self.rf_inicio = DateEntry(filtros, date_pattern='yyyy-mm-dd'); self.rf_inicio.grid(row=0, column=1)
        ttk.Label(filtros, text="Fecha final:").grid(row=0, column=2, padx=5, pady=5)
        self.rf_fin    = DateEntry(filtros, date_pattern='yyyy-mm-dd'); self.rf_fin.grid(row=0, column=3)
        ttk.Label(filtros, text="Estado:").grid(row=0, column=4, padx=5, pady=5)
        self.rf_estado = ttk.Combobox(filtros, values=["Todos","pendiente","confirmada","cancelada","completada"], state="readonly")
        self.rf_estado.set("Todos"); self.rf_estado.grid(row=0, column=5)

        ttk.Button(filtros, text="Generar", command=lambda: self._gen_rep_fecha(tree)).grid(row=0, column=6, padx=10)
        # Export buttons
        btn_frame = ttk.Frame(filtros); btn_frame.grid(row=1, column=0, columnspan=7, pady=5)
        ttk.Button(btn_frame, text="Exportar CSV", command=lambda:self._export_csv(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar PDF", command=lambda:self._export_pdf(tree)).pack(side=tk.LEFT, padx=5)

        self.reportes_tree = tree

    def _gen_rep_fecha(self, tree):
        f1, f2 = self.rf_inicio.get_date(), self.rf_fin.get_date()
        estado = self.rf_estado.get()
        q = """
            SELECT r.id, c.nombre, u.nombre, r.fecha, r.hora_inicio, r.hora_fin, r.duracion, r.estado, COALESCE(p.total,0)
            FROM reserva r
            JOIN cancha c ON r.id_cancha = c.id
            JOIN usuario u ON r.id_usuario = u.id
            LEFT JOIN pago p ON p.id_reserva = r.id
            WHERE r.fecha BETWEEN %s AND %s
        """
        params = [f1, f2]
        if estado!="Todos":
            q += " AND r.estado=%s"; params.append(estado)
        q += " ORDER BY r.fecha, r.hora_inicio"
        self.cursor.execute(q, params)
        datos = self.cursor.fetchall()
        for iid in tree.get_children(): tree.delete(iid)
        for row in datos: tree.insert("",tk.END,values=row)

    def _export_csv(self, tree):
        items = tree.get_children()
        if not items:
            messagebox.showwarning("Atención","No hay datos")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not fp: return
        with open(fp,"w",newline="",encoding="utf-8") as f:
            w = csv.writer(f)
            headers = [tree.heading(c)["text"] for c in tree["columns"]]
            w.writerow(headers)
            for iid in items:
                w.writerow(tree.item(iid)["values"])
        messagebox.showinfo("Éxito",f"Guardado en {fp}")

    def _export_pdf(self, tree):
        items = tree.get_children()
        if not items:
            messagebox.showwarning("Atención","No hay datos")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not fp: return
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial",size=10)
        headers = [tree.heading(c)["text"] for c in tree["columns"]]
        widths = [pdf.w/len(headers)]*len(headers)
        for h,w in zip(headers,widths):
            pdf.cell(w,8,txt=h,border=1)
        pdf.ln()
        for iid in items:
            for val,w in zip(tree.item(iid)["values"],widths):
                pdf.cell(w,8,txt=str(val),border=1)
            pdf.ln()
        pdf.output(fp)
        messagebox.showinfo("Éxito",f"PDF generado en {fp}")

    # 2. Pestaña de gráficas
    def crear_pestaña_graficas(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Gráficas")

        op = ttk.LabelFrame(tab, text="Opciones", padding=10)
        op.pack(fill=tk.X, pady=5)
        ttk.Label(op, text="Tipo:").grid(row=0,column=0,padx=5)
        self.gg_tipo = ttk.Combobox(op, values=["Reservas por día","Ingresos por cancha","Uso de servicios","Estado de reservas"], state="readonly")
        self.gg_tipo.set("Reservas por día"); self.gg_tipo.grid(row=0,column=1,padx=5)
        ttk.Label(op, text="Fecha inicio:").grid(row=0,column=2,padx=5)
        self.gg_fi = DateEntry(op, date_pattern='yyyy-mm-dd'); self.gg_fi.grid(row=0,column=3)
        ttk.Label(op, text="Fecha fin:").grid(row=0,column=4,padx=5)
        self.gg_ff = DateEntry(op, date_pattern='yyyy-mm-dd'); self.gg_ff.grid(row=0,column=5)
        ttk.Button(op, text="Generar", command=self._gen_grafico).grid(row=0,column=6,padx=10)

        self.gg_frame = ttk.Frame(tab); self.gg_frame.pack(fill=tk.BOTH, expand=True)

    def _gen_grafico(self):
        for wid in self.gg_frame.winfo_children(): wid.destroy()
        fig = plt.Figure(figsize=(8,6), dpi=100); ax = fig.add_subplot(111)
        f1, f2 = self.gg_fi.get_date(), self.gg_ff.get_date()
        tipo = self.gg_tipo.get()
        if tipo=="Reservas por día":
            q = "SELECT fecha, COUNT(*) FROM reserva WHERE fecha BETWEEN %s AND %s GROUP BY fecha ORDER BY fecha"
            self.cursor.execute(q,(f1,f2))
            fechas, vals = zip(*self.cursor.fetchall() or [([],[])])
            ax.bar(fechas, vals); ax.set_title(tipo)
        elif tipo=="Ingresos por cancha":
            q = """SELECT c.nombre, SUM(p.total) FROM reserva r
                   JOIN cancha c ON r.id_cancha=c.id
                   JOIN pago p ON p.id_reserva=r.id
                   WHERE r.fecha BETWEEN %s AND %s GROUP BY c.nombre"""
            self.cursor.execute(q,(f1,f2))
            names, vals = zip(*self.cursor.fetchall() or [([],[])])
            ax.bar(names, [float(v) for v in vals]); ax.set_title(tipo)
        elif tipo=="Uso de servicios":
            q = """SELECT sa.descripcion, COUNT(*) FROM reserva_servicio rs
                   JOIN servicio_adicional sa ON rs.id_servicio=sa.id
                   JOIN reserva r ON r.id=rs.id_reserva
                   WHERE r.fecha BETWEEN %s AND %s GROUP BY sa.descripcion"""
            self.cursor.execute(q,(f1,f2))
            labels, vals = zip(*self.cursor.fetchall() or [([],[])])
            ax.pie(vals, labels=labels, autopct='%1.1f%%'); ax.set_title(tipo)
        else:
            q = "SELECT estado, COUNT(*) FROM reserva WHERE fecha BETWEEN %s AND %s GROUP BY estado"
            self.cursor.execute(q,(f1,f2))
            labels, vals = zip(*self.cursor.fetchall() or [([],[])])
            ax.pie(vals, labels=labels, autopct='%1.1f%%'); ax.set_title(tipo)

        canvas = FigureCanvasTkAgg(fig, master=self.gg_frame)
        canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # 3. Pestaña SQL
    def crear_pestaña_sql(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="SQL")
        frame = ttk.LabelFrame(tab, text="Ingresar consulta", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        self.sql_text = tk.Text(frame, height=4)
        self.sql_text.pack(fill=tk.X, padx=5)
        btnf = ttk.Frame(frame); btnf.pack(fill=tk.X)
        ttk.Button(btnf, text="Ejecutar", command=self._exec_sql).pack(side=tk.LEFT,padx=5)
        ttk.Button(btnf, text="Limpiar", command=lambda:self.sql_text.delete("1.0",tk.END)).pack(side=tk.LEFT)

        self.sql_tree = ttk.Treeview(tab)
        sb = ttk.Scrollbar(tab, command=self.sql_tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.sql_tree.configure(yscrollcommand=sb.set)
        self.sql_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _exec_sql(self):
        q = self.sql_text.get("1.0",tk.END).strip()
        if not q:
            messagebox.showwarning("Atención","Escriba una consulta")
            return
        try:
            self.cursor.execute(q)
            cols = [d[0] for d in self.cursor.description]
            self.sql_tree["columns"] = cols
            for c in cols:
                self.sql_tree.heading(c,text=c); self.sql_tree.column(c,width=100)
            for iid in self.sql_tree.get_children():
                self.sql_tree.delete(iid)
            for row in self.cursor.fetchall():
                self.sql_tree.insert("",tk.END,values=row)
        except Exception as e:
            messagebox.showerror("Error SQL",str(e))

    # --- Reportes específicos (del segundo archivo) ---
    def ejecutar_y_mostrar(self, tree, query, params):
        try:
            self.conn.rollback()
        except: pass
        try:
            self.cursor.execute(query, params)
            filas = self.cursor.fetchall()
            for iid in tree.get_children(): tree.delete(iid)
            for fila in filas: tree.insert("",tk.END,values=fila)
        except Exception as e:
            messagebox.showerror("Error al generar reporte", str(e))

    def crear_reporte_ingresos(self):
        filtros, tree = self.crear_pestana_base("Ingresos por Cancha", ["cancha","total"], [300,200])
        # filtros...
        ttk.Label(filtros, text="Fecha inicio:").grid(row=0,column=0)
        fi = DateEntry(filtros, date_pattern='yyyy-mm-dd'); fi.grid(row=0,column=1)
        ttk.Label(filtros, text="Fecha fin:").grid(row=0,column=2)
        ff = DateEntry(filtros, date_pattern='yyyy-mm-dd'); ff.grid(row=0,column=3)
        ttk.Label(filtros, text="Cancha:").grid(row=1,column=0)
        cb = ttk.Combobox(filtros, state="readonly"); cb.grid(row=1,column=1,columnspan=3,sticky="w")
        # cargar canchas
        self.cursor.execute("SELECT id,nombre FROM cancha ORDER BY nombre")
        cb['values'] = ['Todas'] + [f"{n} (ID:{i})" for i,n in self.cursor.fetchall()]
        ttk.Button(filtros, text="Generar", command=lambda:
                   self._gen_ingresos(fi,ff,cb,tree)).grid(row=2,column=0,columnspan=4,pady=6)

    def _gen_ingresos(self, fi, ff, cb, tree):
        f1, f2 = fi.get_date(), ff.get_date()
        cancha = cb.get(); params=[f1,f2]
        q = """SELECT c.nombre, SUM(p.total) FROM pago p
               JOIN reserva r ON p.id_reserva=r.id
               JOIN cancha c ON r.id_cancha=c.id
               WHERE r.fecha BETWEEN %s AND %s"""
        if cancha and cancha!="Todas":
            cid=int(cancha.split("ID:")[1].rstrip(")")); q+=" AND c.id=%s"; params.append(cid)
        q+=" GROUP BY c.nombre ORDER BY SUM(p.total) DESC"
        self.ejecutar_y_mostrar(tree,q,params)

    def crear_reporte_servicios(self):
        filtros, tree = self.crear_pestana_base("Uso de Servicios", ["servicio","usos"], [300,200])
        ttk.Label(filtros, text="Fecha inicio:").grid(row=0,column=0)
        fi = DateEntry(filtros, date_pattern='yyyy-mm-dd'); fi.grid(row=0,column=1)
        ttk.Label(filtros, text="Fecha fin:").grid(row=0,column=2)
        ff = DateEntry(filtros, date_pattern='yyyy-mm-dd'); ff.grid(row=0,column=3)
        ttk.Label(filtros, text="Servicio:").grid(row=1,column=0)
        scb = ttk.Combobox(filtros, state="readonly"); scb.grid(row=1,column=1)
        ttk.Label(filtros, text="Usuario ID:").grid(row=1,column=2)
        usr = ttk.Entry(filtros); usr.grid(row=1,column=3)
        ttk.Label(filtros, text="Cancha:").grid(row=2,column=0)
        ccb = ttk.Combobox(filtros, state="readonly"); ccb.grid(row=2,column=1)
        # valores
        self.cursor.execute("SELECT id,descripcion FROM servicio_adicional")
        scb['values'] = ['Todos'] + [f"{d} (ID:{i})" for i,d in self.cursor.fetchall()]
        self.cursor.execute("SELECT id,nombre FROM cancha")
        ccb['values'] = ['Todas'] + [f"{n} (ID:{i})" for i,n in self.cursor.fetchall()]
        ttk.Button(filtros, text="Generar", command=lambda:
                   self._gen_servicios(fi,ff,scb,usr,ccb,tree)).grid(row=3,column=0,columnspan=4,pady=6)

    def _gen_servicios(self, fi, ff, scb, usr, ccb, tree):
        f1, f2 = fi.get_date(), ff.get_date()
        params=[f1,f2]; q = """SELECT sa.descripcion, COUNT(*) FROM reserva_servicio rs
                 JOIN servicio_adicional sa ON rs.id_servicio=sa.id
                 JOIN reserva r ON r.id=rs.id_reserva
                 WHERE r.fecha BETWEEN %s AND %s"""
        if scb.get()!="Todos":
            sid=int(scb.get().split("ID:")[1].rstrip(")")); q+=" AND sa.id=%s"; params.append(sid)
        if usr.get().strip():
            q+=" AND r.id_usuario=%s"; params.append(int(usr.get().strip()))
        if ccb.get()!="Todas":
            cid=int(ccb.get().split("ID:")[1].rstrip(")")); q+=" AND r.id_cancha=%s"; params.append(cid)
        q+=" GROUP BY sa.descripcion ORDER BY COUNT(*) DESC"
        self.ejecutar_y_mostrar(tree,q,params)

    def crear_reporte_por_usuario(self):
        filtros, tree = self.crear_pestana_base("Reservas por Usuario", ["id","fecha","inicio","fin","estado"], [80,120,120,120,120])
        ttk.Label(filtros, text="Usuario ID:").grid(row=0,column=0)
        uid = ttk.Entry(filtros); uid.grid(row=0,column=1)
        ttk.Label(filtros, text="Fecha inicio:").grid(row=0,column=2)
        fi = DateEntry(filtros, date_pattern='yyyy-mm-dd'); fi.grid(row=0,column=3)
        ttk.Label(filtros, text="Fecha fin:").grid(row=1,column=0)
        ff = DateEntry(filtros, date_pattern='yyyy-mm-dd'); ff.grid(row=1,column=1)
        ttk.Label(filtros, text="Estado:").grid(row=1,column=2)
        est = ttk.Combobox(filtros, state="readonly", values=["Todas","pendiente","confirmada","cancelada"]); est.grid(row=1,column=3)
        ttk.Label(filtros, text="Cancha:").grid(row=2,column=0)
        cb  = ttk.Combobox(filtros, state="readonly"); cb.grid(row=2,column=1)
        self.cursor.execute("SELECT id,nombre FROM cancha")
        cb['values'] = ['Todas'] + [f"{n} (ID:{i})" for i,n in self.cursor.fetchall()]
        ttk.Button(filtros, text="Generar", command=lambda:
                   self._gen_usuario(uid,fi,ff,est,cb,tree)).grid(row=3,column=0,columnspan=4,pady=6)

    def _gen_usuario(self, uid, fi, ff, est, cb, tree):
        params=[]; q="""SELECT r.id,r.fecha,r.hora_inicio AS inicio,r.hora_fin AS fin,r.estado
               FROM reserva r WHERE 1=1"""
        if uid.get().strip():
            q+=" AND r.id_usuario=%s"; params.append(int(uid.get().strip()))
        q+=" AND r.fecha BETWEEN %s AND %s"; params += [fi.get_date(), ff.get_date()]
        if est.get()!="Todas":
            q+=" AND r.estado=%s"; params.append(est.get())
        if cb.get()!="Todas":
            cid=int(cb.get().split("ID:")[1].rstrip(")")); q+=" AND r.id_cancha=%s"; params.append(cid)
        q+=" ORDER BY r.fecha"
        self.ejecutar_y_mostrar(tree,q,params)

    def crear_reporte_duracion(self):
        filtros, tree = self.crear_pestana_base("Duración de Reservas", ["id","duracion","fecha"], [80,120,120])
        ttk.Label(filtros, text="Min. (h):").grid(row=0,column=0)
        dmin = ttk.Spinbox(filtros, from_=0,to=24,width=5); dmin.grid(row=0,column=1)
        ttk.Label(filtros, text="Max. (h):").grid(row=0,column=2)
        dmax = ttk.Spinbox(filtros, from_=0,to=24,width=5); dmax.grid(row=0,column=3)
        ttk.Label(filtros, text="Fecha inicio:").grid(row=1,column=0)
        fi = DateEntry(filtros, date_pattern='yyyy-mm-dd'); fi.grid(row=1,column=1)
        ttk.Label(filtros, text="Fecha fin:").grid(row=1,column=2)
        ff = DateEntry(filtros, date_pattern='yyyy-mm-dd'); ff.grid(row=1,column=3)
        ttk.Label(filtros, text="Cancha:").grid(row=2,column=0)
        cb = ttk.Combobox(filtros, state="readonly"); cb.grid(row=2,column=1)
        self.cursor.execute("SELECT id,nombre FROM cancha")
        cb['values'] = ['Todas'] + [f"{n} (ID:{i})" for i,n in self.cursor.fetchall()]
        ttk.Button(filtros, text="Generar", command=lambda:
                   self._gen_duracion(dmin,dmax,fi,ff,cb,tree)).grid(row=3,column=0,columnspan=4,pady=6)

    def _gen_duracion(self, dmin, dmax, fi, ff, cb, tree):
        q = """SELECT r.id,r.duracion,r.fecha FROM reserva r
               WHERE r.duracion BETWEEN %s AND %s
                 AND r.fecha BETWEEN %s AND %s"""
        params = [float(dmin.get()), float(dmax.get()), fi.get_date(), ff.get_date()]
        if cb.get()!="Todas":
            cid=int(cb.get().split("ID:")[1].rstrip(")")); q+=" AND r.id_cancha=%s"; params.append(cid)
        self.ejecutar_y_mostrar(tree,q,params)

    def crear_reporte_comparativo_mensual(self):
        filtros, tree = self.crear_pestana_base("Comparativo Mensual", ["mes","total"], [120,200])
        ttk.Label(filtros, text="Mes:").grid(row=0,column=0)
        mes = ttk.Spinbox(filtros, from_=1,to=12,width=5); mes.grid(row=0,column=1)
        ttk.Label(filtros, text="Año:").grid(row=0,column=2)
        anio= ttk.Spinbox(filtros, from_=2020,to=2030,width=5); anio.grid(row=0,column=3)
        ttk.Label(filtros, text="Cancha:").grid(row=1,column=0)
        cb = ttk.Combobox(filtros, state="readonly"); cb.grid(row=1,column=1)
        ttk.Label(filtros, text="Usuario ID:").grid(row=1,column=2)
        usr = ttk.Entry(filtros); usr.grid(row=1,column=3)
        ttk.Label(filtros, text="Estado:").grid(row=2,column=0)
        est = ttk.Combobox(filtros, state="readonly", values=["Todas","pendiente","confirmada","cancelada"]); est.grid(row=2,column=1)
        self.cursor.execute("SELECT id,nombre FROM cancha")
        cb['values'] = ['Todas'] + [f"{n} (ID:{i})" for i,n in self.cursor.fetchall()]
        ttk.Button(filtros, text="Generar", command=lambda:
                   self._gen_comparativo(mes,anio,cb,usr,est,tree)).grid(row=3,column=0,columnspan=4,pady=6)

    def _gen_comparativo(self, mes, anio, cb, usr, est, tree):
        m,y = int(mes.get()), int(anio.get())
        q = """SELECT EXTRACT(MONTH FROM fecha) AS mes, COUNT(*) AS total
               FROM reserva r
               WHERE EXTRACT(MONTH FROM fecha)=%s
                 AND EXTRACT(YEAR FROM fecha)=%s"""
        params = [m,y]
        if cb.get()!="Todas":
            cid=int(cb.get().split("ID:")[1].rstrip(")")); q+=" AND r.id_cancha=%s"; params.append(cid)
        if usr.get().strip():
            q+=" AND r.id_usuario=%s"; params.append(int(usr.get().strip()))
        if est.get()!="Todas":
            q+=" AND r.estado=%s"; params.append(est.get())
        q+=" GROUP BY mes ORDER BY mes"
        self.ejecutar_y_mostrar(tree,q,params)


if __name__ == "__main__":
    root = tk.Tk()
    app = MergedReportApp(root)
    root.mainloop()
