import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime, time, timedelta
from psycopg2 import sql
from tkcalendar import DateEntry
#Si se necesita instalar alguna libreria utilizar pip install y el nombre de la libreria que se desea instalar

class ReservaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Reservas")
        self.root.geometry("1000x700")
        
        # Conexión a la base de datos
        self.conn = psycopg2.connect(
            dbname="negroshima",
            user="postgres",
            password="admin",
            host="localhost"
        )
        self.cursor = self.conn.cursor()
        

        self.usuario_actual = None
        self.reserva_seleccionada = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Login 
        self.login_frame = ttk.LabelFrame(self.main_frame, text="Iniciar Sesión / Registro", padding="10")
        self.login_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
    
        self.notebook = ttk.Notebook(self.login_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Login
        self.login_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.login_tab, text="Iniciar Sesión")
        
        ttk.Label(self.login_tab, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(self.login_tab, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_tab, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_tab, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.login_tab, text="Ingresar", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Pestaña de Registro
        self.register_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.register_tab, text="Registrar Usuario")
        
        ttk.Label(self.register_tab, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5)
        self.reg_nombre_entry = ttk.Entry(self.register_tab, width=30)
        self.reg_nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.register_tab, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.reg_email_entry = ttk.Entry(self.register_tab, width=30)
        self.reg_email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.register_tab, text="Contraseña:").grid(row=2, column=0, padx=5, pady=5)
        self.reg_password_entry = ttk.Entry(self.register_tab, width=30, show="*")
        self.reg_password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.register_tab, text="Confirmar contraseña:").grid(row=3, column=0, padx=5, pady=5)
        self.reg_confirm_password_entry = ttk.Entry(self.register_tab, width=30, show="*")
        self.reg_confirm_password_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(self.register_tab, text="Teléfono:").grid(row=4, column=0, padx=5, pady=5)
        self.reg_telefono_entry = ttk.Entry(self.register_tab, width=30)
        self.reg_telefono_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Button(self.register_tab, text="Registrarse", command=self.registrar_usuario).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Reserva 
        self.reserva_frame = ttk.LabelFrame(self.main_frame, text="Gestión de Reservas", padding="10")
        
        # Crear reserva
        self.crear_reserva_frame = ttk.LabelFrame(self.reserva_frame, text="Nueva Reserva", padding="10")
        self.crear_reserva_frame.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)
        
        # cancha
        ttk.Label(self.crear_reserva_frame, text="Cancha:").grid(row=0, column=0, padx=5, pady=5)
        self.cancha_combobox = ttk.Combobox(self.crear_reserva_frame, state="readonly", width=27)
        self.cancha_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.cancha_combobox.bind("<<ComboboxSelected>>", self.actualizar_fechas_disponibles)
        
        # Fecha
        ttk.Label(self.crear_reserva_frame, text="Fecha:").grid(row=1, column=0, padx=5, pady=5)
        self.fecha_entry = DateEntry(
            self.crear_reserva_frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            mindate=datetime.now()
        )
        self.fecha_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Hora inicio
        ttk.Label(self.crear_reserva_frame, text="Hora inicio:").grid(row=2, column=0, padx=5, pady=5)
        self.hora_inicio_combobox = ttk.Combobox(self.crear_reserva_frame, state="readonly", width=8)
        self.hora_inicio_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Hora fin
        ttk.Label(self.crear_reserva_frame, text="Hora fin:").grid(row=3, column=0, padx=5, pady=5)
        self.hora_fin_combobox = ttk.Combobox(self.crear_reserva_frame, state="readonly", width=8)
        self.hora_fin_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Servicios adicionales
        ttk.Label(self.crear_reserva_frame, text="Servicios adicionales:").grid(row=4, column=0, padx=5, pady=5)
        self.servicios_listbox = tk.Listbox(self.crear_reserva_frame, selectmode=tk.MULTIPLE, height=4, width=30)
        self.servicios_listbox.grid(row=4, column=1, padx=5, pady=5)
        
        # Botón  reserva
        ttk.Button(self.crear_reserva_frame, text="Crear Reserva", command=self.crear_reserva).grid(row=5, column=0, columnspan=2, pady=10)
        
        # reservas
        self.mis_reservas_frame = ttk.LabelFrame(self.reserva_frame, text="Mis Reservas", padding="10")
        self.mis_reservas_frame.grid(row=0, column=1, sticky="nsew", pady=5, padx=5)
        
        # Treeview reservas
        self.reservas_tree = ttk.Treeview(self.mis_reservas_frame, columns=("id", "cancha", "fecha", "hora_inicio", "hora_fin", "estado"), show="headings")
        self.reservas_tree.heading("id", text="ID")
        self.reservas_tree.heading("cancha", text="Cancha")
        self.reservas_tree.heading("fecha", text="Fecha")
        self.reservas_tree.heading("hora_inicio", text="Hora Inicio")
        self.reservas_tree.heading("hora_fin", text="Hora Fin")
        self.reservas_tree.heading("estado", text="Estado")
        self.reservas_tree.column("id", width=50)
        self.reservas_tree.column("cancha", width=150)
        self.reservas_tree.column("fecha", width=100)
        self.reservas_tree.column("hora_inicio", width=80)
        self.reservas_tree.column("hora_fin", width=80)
        self.reservas_tree.column("estado", width=100)
        self.reservas_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.mis_reservas_frame, orient="vertical", command=self.reservas_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.reservas_tree.configure(yscrollcommand=scrollbar.set)
        
        #cancelar reserva
        ttk.Button(self.mis_reservas_frame, text="Cancelar Reserva", command=self.cancelar_reserva).grid(row=1, column=0, pady=10)
        
      
        self.reserva_frame.columnconfigure(0, weight=1)
        self.reserva_frame.columnconfigure(1, weight=1)
        self.reserva_frame.rowconfigure(0, weight=1)
        
       
        self.reserva_frame.grid_remove()
       
        self.reservas_tree.bind("<<TreeviewSelect>>", self.seleccionar_reserva)
    
    #LOGIN
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        #Revisa que hayan datos
        if not email or not password:
            messagebox.showerror("Error", "Por favor ingrese email y contraseña")
            return
        #Prueba iniciar sesión desde la base de datos
        try:
            query = sql.SQL("SELECT id, nombre FROM usuario WHERE email = %s AND password_hash = %s")
            self.cursor.execute(query, (email, password))
            resultado = self.cursor.fetchone()
            
            if resultado:
                self.usuario_actual = {"id": resultado[0], "nombre": resultado[1]}
                messagebox.showinfo("Éxito", f"Bienvenido {resultado[1]}")
                self.login_frame.grid_remove()
                self.reserva_frame.grid()
                self.cargar_datos_iniciales()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {str(e)}")
    
    #Crear usuario
    def registrar_usuario(self):
        nombre = self.reg_nombre_entry.get()
        email = self.reg_email_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        telefono = self.reg_telefono_entry.get()
        
        # revisa que este todo
        if not all([nombre, email, password, confirm_password]):
            messagebox.showerror("Error", "Por favor complete todos los campos obligatorios")
            return
        #Comprueba los passwords
        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        try:
            # Verificar si el email ya existe
            self.cursor.execute("SELECT 1 FROM usuario WHERE email = %s", (email,))
            if self.cursor.fetchone():
                messagebox.showerror("Error", "El email ya está registrado")
                return
            
            query = """
            INSERT INTO usuario (nombre, email, password_hash, estado)
            VALUES (%s, %s, %s, 'activo')
            RETURNING id
            """
            self.cursor.execute(query, (nombre, email, password))
            user_id = self.cursor.fetchone()[0]
            
           
            if telefono:
                query = "INSERT INTO usuario_telefono (id_usuario, telefono) VALUES (%s, %s)"
                self.cursor.execute(query, (user_id, telefono))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            
       
            self.reg_nombre_entry.delete(0, tk.END)
            self.reg_email_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_confirm_password_entry.delete(0, tk.END)
            self.reg_telefono_entry.delete(0, tk.END)
            
            # regresa al login
            self.notebook.select(self.login_tab)
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {str(e)}")
    
    def cargar_datos_iniciales(self):
        
        self.cursor.execute("SELECT id, nombre FROM cancha ORDER BY nombre")
        canchas = self.cursor.fetchall()
        self.cancha_combobox["values"] = [f"{nombre} (ID: {id})" for id, nombre in canchas]
        self.cursor.execute("SELECT id, descripcion, precio FROM servicio_adicional ORDER BY descripcion")
        servicios = self.cursor.fetchall()
        self.servicios_listbox.delete(0, tk.END)
        for id, descripcion, precio in servicios:
            self.servicios_listbox.insert(tk.END, f"{descripcion} (${precio:.2f})")
        self.actualizar_mis_reservas()
    
    def actualizar_mis_reservas(self):
        if not self.usuario_actual:
            return
        
        for item in self.reservas_tree.get_children():
            self.reservas_tree.delete(item)
        
        
        


        query = """
        SELECT r.id, c.nombre, r.fecha, r.hora_inicio, r.hora_fin, r.estado 
        FROM reserva r JOIN cancha c ON r.id_cancha = c.id 
        WHERE r.id_usuario = %s
        ORDER BY r.fecha, r.hora_inicio
        """
        self.cursor.execute(query, (self.usuario_actual["id"],))
        reservas = self.cursor.fetchall()
        
        for reserva in reservas:
            self.reservas_tree.insert("", tk.END, values=reserva)
    
    def actualizar_fechas_disponibles(self, event=None):
       
        self.actualizar_horas_disponibles()
    
    def actualizar_horas_disponibles(self):
        if not self.cancha_combobox.get():
            return
        
        try:
           
            cancha_str = self.cancha_combobox.get()
            cancha_id = int(cancha_str.split("(ID: ")[1].rstrip(")"))
            
            # horarios
            query = """
            SELECT h.hora_inicio, h.hora_fin 
            FROM horario h 
            JOIN cancha_horario ch ON h.id = ch.id_horario 
            WHERE ch.id_cancha = %s
            ORDER BY h.hora_inicio
            """
            self.cursor.execute(query, (cancha_id,))
            horarios = self.cursor.fetchall()
            
            if not horarios:
                messagebox.showwarning("Advertencia", "No hay horarios definidos para esta cancha")
                return
            
            # horarios en la combobox
            horas_disponibles = []
            for hora_inicio, hora_fin in horarios:
                current_time = hora_inicio
                while current_time < hora_fin:
                    horas_disponibles.append(current_time.strftime("%H:%M"))
                    current_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()
            
            self.hora_inicio_combobox["values"] = hora_inicio
            self.hora_fin_combobox["values"] = hora_fin
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar horarios: {str(e)}")
    
    def crear_reserva(self):
        if not all([
            self.cancha_combobox.get(),
            self.hora_inicio_combobox.get(),
            self.hora_fin_combobox.get()
        ]):
            messagebox.showerror("Error", "Por favor complete todos los campos obligatorios")
            return
        
        try:

            cancha_str = self.cancha_combobox.get()
            cancha_id = int(cancha_str.split("(ID: ")[1].rstrip(")"))
            fecha = self.fecha_entry.get_date().strftime("%Y-%m-%d")
            hora_inicio = self.hora_inicio_combobox.get()
            hora_fin = self.hora_fin_combobox.get()
            
            # Verificar que hora fin sea mayor que hora inicio
            if hora_inicio >= hora_fin:
                messagebox.showerror("Error", "La hora de fin debe ser posterior a la hora de inicio")
                return
            

            servicios_seleccionados = [self.servicios_listbox.get(i) for i in self.servicios_listbox.curselection()]
            servicios_ids = [int(s.split("(ID: ")[1].split(")")[0]) for s in servicios_seleccionados if "(ID:" in s]
            
            query = "INSERT INTO reserva (id_usuario, id_cancha, fecha, hora_inicio, hora_fin, duracion, estado) VALUES (%s, %s, %s, %s, %s, '1.00','pendiente') RETURNING id"
            
            print(self.usuario_actual["id"])
            print(cancha_id)
            print(fecha)
            print(hora_inicio)
            print(hora_fin)
            self.cursor.execute(query, (
                self.usuario_actual["id"],
                cancha_id,
                fecha,
                hora_inicio,
                hora_fin
            ))
            reserva_id = self.cursor.fetchone()[0]
            
            for servicio_id in servicios_ids:
                query = "INSERT INTO reserva_servicio (id_reserva, id_servicio) VALUES (%s, %s)"
                self.cursor.execute(query, (reserva_id, servicio_id))
           
           
           #ARREGLAR EL PAGO NO SIRVE 
           # query = "INSERT INTO pago (id_reserva) VALUES (%s)"
            #self.cursor.execute(query, (reserva_id,))
            
            self.conn.commit()
           
           
           
           
           
           
            messagebox.showinfo("Éxito", "Reserva creada correctamente")
            self.actualizar_mis_reservas()
            self.limpiar_formulario()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"No se pudo crear la reserva: {str(e)}")
    
    def limpiar_formulario(self):
        self.hora_inicio_combobox.set("")
        self.hora_fin_combobox.set("")
        self.servicios_listbox.selection_clear(0, tk.END)
    
    def seleccionar_reserva(self, event):
        selected_item = self.reservas_tree.focus()
        if selected_item:
            self.reserva_seleccionada = self.reservas_tree.item(selected_item)["values"]
    
    def cancelar_reserva(self):
        if not self.reserva_seleccionada:
            messagebox.showerror("Error", "Por favor seleccione una reserva para cancelar")
            return
        
        reserva_id = self.reserva_seleccionada[0]
        estado_actual = self.reserva_seleccionada[5]
        
        if estado_actual == "cancelada":
            messagebox.showwarning("Advertencia", "Esta reserva ya está cancelada")
            return
        
        confirmacion = messagebox.askyesno("Confirmar", f"¿Está seguro que desea cancelar la reserva ID: {reserva_id}?")
        if confirmacion:
            try:
                query = "UPDATE reserva SET estado = 'cancelada' WHERE id = %s"
                self.cursor.execute(query, (reserva_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Reserva cancelada correctamente")
                self.actualizar_mis_reservas()
                self.reserva_seleccionada = None
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", f"No se pudo cancelar la reserva: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservaApp(root)
    root.mainloop()