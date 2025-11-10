import customtkinter as ctk
from tkinter import CENTER, messagebox
import random as rd
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# ---------------- CONFIGURACIÓN GENERAL ----------------
ctk.set_appearance_mode("light")  # modo claro

grafo = nx.Graph()
recorridos = []

root = ctk.CTk()
root.title("Problema del Agente Viajero")
root.geometry("1000x600")
root.configure(fg_color="#f8f1e5")

# ---------------- LÓGICA ----------------

def generar_grafo_aleatorio(nodos, completo=True):
    global grafo
    grafo = nx.Graph()
    adj = [[0]*nodos for _ in range(nodos)]

    if completo:
        for i in range(nodos):
            for j in range(i+1, nodos):
                peso = rd.randint(9, 100)
                grafo.add_edge(i, j, weight=peso)
                adj[i][j] = adj[j][i] = peso
    else:
        for _ in range(3*nodos + 1):
            u, v = rd.sample(range(nodos), 2)
            peso = rd.randint(9, 100)
            grafo.add_edge(u, v, weight=peso)
            adj[u][v] = adj[v][u] = peso
    return adj

def buscar_ciclos_hamiltonianos(nodos, adj):
    visited, ciclos = [0]*nodos, []
    recorridos.clear()

    def dfs(nodo, camino, suma):
        for i in range(nodos):
            if adj[nodo][i] == 0:
                continue
            if not visited[i] and len(camino) < nodos:
                visited[i] = 1
                dfs(i, camino + [i], suma + adj[nodo][i])
                visited[i] = 0
            elif i == 0 and len(camino) == nodos:
                ciclos.append(camino + [0])
                recorridos.append((suma, camino + [0]))

    visited[0] = 1
    dfs(0, [0], 0)
    return ciclos

def generar_imagen_grafo(G, titulo="Grafo"):
    pos = nx.spring_layout(G, seed=42)
    colores_arista = [G[u][v].get('color', 'black') for u, v in G.edges()]
    fig, ax = plt.subplots(figsize=(6, 6))
    nx.draw(G, pos, with_labels=True, node_size=800, node_color="lightblue",
            edge_color=colores_arista, width=2, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'), ax=ax)
    plt.title(titulo, fontsize=16, fontweight='bold')

    # Guardar imagen en memoria
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

def dibujar_grafo(G, titulo="Grafo"):
    """
    Dibuja el grafo en una ventana de CustomTkinter
    """
    ventana_grafo = ctk.CTkToplevel(root)
    ventana_grafo.title("Visualización del Grafo")
    ventana_grafo.geometry("700x750")
    ventana_grafo.configure(fg_color="#f8f1e5")

    # Título
    ctk.CTkLabel(ventana_grafo, text=f"🌐 {titulo}",
                 font=("Montserrat", 28, "bold"),
                 text_color="#815c36").place(relx=0.5, rely=0.08, anchor=CENTER)

    # Generar imagen del grafo
    imagen = generar_imagen_grafo(G, titulo)
    img_ctk = ctk.CTkImage(light_image=imagen, size=(600, 600))

    # Mostrar imagen
    ctk.CTkLabel(ventana_grafo, image=img_ctk, text="").place(relx=0.5, rely=0.52, anchor=CENTER)

    # Botón cerrar
    ctk.CTkButton(ventana_grafo, text="Cerrar ventana",
                  font=("Montserrat", 16, "bold"),
                  fg_color="#4b70ff", text_color="white",
                  width=220, height=45, corner_radius=30,
                  command=ventana_grafo.destroy).place(relx=0.5, rely=0.93, anchor=CENTER)

def mostrar_menor_recorrido():
    if not recorridos:
        messagebox.showwarning("Advertencia", "No se han generado recorridos aún.")
        return
    
    menor = min(recorridos, key=lambda x: x[0])
    costo_total = menor[0]
    camino = menor[1]
    
    # Crear ventana personalizada
    ventana_optimo = ctk.CTkToplevel(root)
    ventana_optimo.title("Ciclo Hamiltoniano Óptimo")
    ventana_optimo.geometry("1000x700")
    ventana_optimo.configure(fg_color="#f8f1e5")

    # Título
    ctk.CTkLabel(ventana_optimo, text=f"🏆 Ciclo Hamiltoniano Óptimo",
                 font=("Montserrat", 28, "bold"),
                 text_color="#815c36").place(relx=0.5, rely=0.08, anchor=CENTER)

    # Generar imagen del grafo con el camino resaltado
    copia = grafo.copy()
    for i in range(len(camino)-1):
        copia[camino[i]][camino[i+1]]["color"] = "red"
    
    imagen = generar_imagen_grafo(copia, f"Costo total: {costo_total}")
    img_ctk = ctk.CTkImage(light_image=imagen, size=(500, 500))

    # Mostrar imagen del grafo a la izquierda
    ctk.CTkLabel(ventana_optimo, image=img_ctk, text="").place(relx=0.28, rely=0.52, anchor=CENTER)

    # Panel derecho con información de la ruta
    frame_info = ctk.CTkFrame(ventana_optimo, width=380, height=550, 
                              fg_color="#ffffff", corner_radius=20)
    frame_info.place(relx=0.72, rely=0.52, anchor=CENTER)

    # Título del panel
    ctk.CTkLabel(frame_info, text="📍 Ruta Óptima",
                 font=("Montserrat", 24, "bold"),
                 text_color="#815c36").place(relx=0.5, rely=0.08, anchor=CENTER)

    # Construir texto de la ruta
    ruta_texto = " → ".join(str(nodo) for nodo in camino)
    
    # Construir texto de las distancias
    distancias = []
    for i in range(len(camino)-1):
        peso = grafo[camino[i]][camino[i+1]]['weight']
        distancias.append(str(peso))
    
    distancias_texto = " → ".join(distancias)

    # Textbox para mostrar la información
    info_box = ctk.CTkTextbox(frame_info, width=340, height=420,
                              fg_color="#f8f1e5", text_color="#7e5c38",
                              font=("Consolas", 16), corner_radius=15)
    info_box.place(relx=0.5, rely=0.55, anchor=CENTER)

    contenido = f"""
╔══════════════════════════════════╗
      INFORMACIÓN DEL RECORRIDO
╚══════════════════════════════════╝

🎯 Costo Total: {costo_total}

📌 Secuencia de Nodos:
{ruta_texto}

📏 Distancias entre Nodos:
{distancias_texto}

📊 Estadísticas:
• Total de nodos: {len(camino) - 1}
• Total de aristas: {len(camino) - 1}
• Distancia promedio: {costo_total / (len(camino) - 1):.2f}
"""
    
    info_box.insert("0.0", contenido)
    info_box.configure(state="disabled")

    # Botón cerrar
    ctk.CTkButton(ventana_optimo, text="Cerrar ventana",
                  font=("Montserrat", 16, "bold"),
                  fg_color="#4b70ff", text_color="white",
                  width=220, height=45, corner_radius=30,
                  command=ventana_optimo.destroy).place(relx=0.5, rely=0.93, anchor=CENTER)

def mostrar_grafo_y_matriz():
    if grafo.number_of_nodes() == 0:
        messagebox.showwarning("Advertencia", "Primero genera un grafo.")
        return

    ventana_grafo = ctk.CTkToplevel(root)
    ventana_grafo.title("Visualización del Grafo")
    ventana_grafo.geometry("950x650")
    ventana_grafo.configure(fg_color="#f8f1e5")

    # Generar imagen del grafo
    imagen = generar_imagen_grafo(grafo, "Grafo generado")
    img_ctk = ctk.CTkImage(light_image=imagen, size=(450, 450))

    ctk.CTkLabel(ventana_grafo, text="🌐 Grafo generado",
                 font=("Montserrat", 26, "bold"),
                 text_color="#815c36").place(relx=0.5, rely=0.08, anchor=CENTER)

    ctk.CTkLabel(ventana_grafo, image=img_ctk, text="").place(relx=0.3, rely=0.55, anchor=CENTER)

    # Matriz de adyacencia
    matriz_texto = "Matriz de adyacencia:\n\n"
    nodos = list(grafo.nodes())
    matriz = nx.to_numpy_array(grafo, dtype=int)
    for i, fila in enumerate(matriz):
        matriz_texto += f"{nodos[i]:2}: " + "  ".join(map(lambda x: f"{x:2}", fila)) + "\n"

    texto_box = ctk.CTkTextbox(ventana_grafo, width=350, height=400,
                               fg_color="#ffffff", text_color="#7e5c38",
                               font=("Consolas", 16), corner_radius=15)
    texto_box.place(relx=0.73, rely=0.55, anchor=CENTER)
    texto_box.insert("0.0", matriz_texto)
    texto_box.configure(state="disabled")

    ctk.CTkButton(ventana_grafo, text="Cerrar ventana",
                  font=("Montserrat", 16, "bold"),
                  fg_color="#4b70ff", text_color="white",
                  width=220, height=45, corner_radius=30,
                  command=ventana_grafo.destroy).place(relx=0.5, rely=0.93, anchor=CENTER)


# ---------------- FUNCIONES DE INTERFAZ ----------------

def abrir_instrucciones():
    instrucciones = ctk.CTkToplevel(root)
    instrucciones.title("Instrucciones")
    instrucciones.geometry("800x500")
    instrucciones.configure(fg_color="#f8f1e5")

    # Título
    ctk.CTkLabel(
        instrucciones,
        text="📑 Instrucciones",
        font=("Montserrat", 36, "bold"),
        text_color="#815c36"
    ).place(relx=0.5, rely=0.15, anchor=CENTER)

    # Textito
    texto = (
        "¡¡Bienvenido al programa del Agente Viajero!!\n\n"
        "Para usar el simulador, debes seguir los siguientes pasos:\n"
        "1. Presiona [Empezar simulación] para generar un grafo.\n"
        "2. Selecciona [Generar grafo] y elige si deseas un grafo aleatorio o manual.\n"
        "3. Presiona [Mostrar grafo] para observar el grafo generado con sus respectivas relaciones.\n"
        "4. A continuación, presiona [Buscar ciclo más óptimo] para ver los ciclos hamiltoneanos existentes y obtener el de menor costo.\n\n"
        "Dato curioso: Mientras más nodos tenga el grafo, mayor será el tiempo de búsqueda."
    )

    ctk.CTkTextbox(
        instrucciones,
        width=600,
        height=280,
        fg_color="#ffffff",
        text_color="#7e5c38",
        font=("Montserrat", 18),
        corner_radius=20,
        wrap="word"
    ).place(relx=0.5, rely=0.50, anchor=CENTER)

    textbox = instrucciones.winfo_children()[-1]
    textbox.insert("0.0", texto)
    textbox.configure(state="disabled")

    # Botón volver
    ctk.CTkButton(
        instrucciones,
        text="Volver al menú",
        font=("Montserrat", 16, "bold"),
        fg_color="#afde72",
        hover_color="#6688ff",
        text_color="white",
        width=200,
        height=45,
        corner_radius=50,
        command=instrucciones.destroy
    ).place(relx=0.5, rely=0.88, anchor=CENTER)


def abrir_creditos():
    creditos = ctk.CTkToplevel(root)
    creditos.title("Créditos")
    creditos.geometry("800x500")
    creditos.configure(fg_color="#f8f1e5")

    # Título
    ctk.CTkLabel(
        creditos,
        text="🎓 Créditos",
        font=("Montserrat", 36, "bold"),
        text_color="#815c36"
    ).place(relx=0.5, rely=0.15, anchor=CENTER)

    # Textito
    texto = (
        "\n  Desarrollado para el curso de Matemática Computacional - 1AMA0475\n"
        "                  ♨️Universidad Peruana de Ciencias Aplicadas           \n\n"
        "       👥 Integrantes:\n"
        "         • Asmat Alminco, Martín Alejandro\n"
        "         • Barrientos Villalta, Vanessa Jazmín\n"
        "         • Del Castillo Mendoza, Matías Javier\n"
        "         • Gallardo Morales, Carla Alejandra\n"
        "         • Ríos Hasegawa, Vivianne Fátima\n\n"
        "                                                   2025-02                                 "
    )

    ctk.CTkTextbox(
        creditos,
        width=600,
        height=280,
        fg_color="#ffffff",
        text_color="#7e5c38",
        font=("Montserrat", 18),
        corner_radius=20,
        wrap="word"
    ).place(relx=0.5, rely=0.50, anchor=CENTER)

    textbox = creditos.winfo_children()[-1]
    textbox.insert("0.0", texto)
    textbox.configure(state="disabled")

    # Botón volver
    ctk.CTkButton(
        creditos,
        text="Volver al menú",
        font=("Montserrat", 16, "bold"),
        fg_color="#4b70ff",
        hover_color="#6688ff",
        text_color="white",
        width=200,
        height=45,
        corner_radius=50,
        command=creditos.destroy
    ).place(relx=0.5, rely=0.88, anchor=CENTER)


# ---------------- BOTONES PRINCIPALES ----------------

def generar_grafo_ui():
    try:
        nodos = int(ctk.CTkInputDialog(text="Ingrese cantidad de nodos (8–16):", title="Configuración").get_input())
        if nodos < 8 or nodos > 16:
            messagebox.showerror("Error", "El número de nodos debe estar entre 8 y 16.")
            return
        tipo = messagebox.askyesno("Tipo de grafo", "¿Deseas un grafo completo aleatorio?\nSí = Completo / No = Parcial")
        adj = generar_grafo_aleatorio(nodos, completo=tipo)
        dibujar_grafo(grafo, "Grafo generado")
        ciclos = buscar_ciclos_hamiltonianos(nodos, adj)
        if not ciclos:
            messagebox.showinfo("Resultado", "No se encontraron ciclos Hamiltonianos.")
        else:
            messagebox.showinfo("Resultado", f"Se encontraron {len(ciclos)} ciclos posibles.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")


# ---------------- BOTONES PRINCIPALES ----------------

def abrir_simulacion():
    ventana_simulacion = ctk.CTkToplevel(root)
    ventana_simulacion.title("Simulación del Agente Viajero")
    ventana_simulacion.geometry("900x550")
    ventana_simulacion.configure(fg_color="#f8f1e5")

    ctk.CTkLabel(ventana_simulacion, text="🎯 Simulación del Agente Viajero",
                 font=("Montserrat", 36, "bold"), text_color="#815c36").place(relx=0.5, rely=0.15, anchor=CENTER)

    # Botones de simulación
    ctk.CTkButton(ventana_simulacion, text="Generar grafo",
                  font=("Montserrat", 20), fg_color="#ff4b4b", hover_color="#ff6666",
                  text_color="white", width=270, height=60, corner_radius=50,
                  command=generar_grafo_ui).place(relx=0.5, rely=0.40, anchor=CENTER)

    ctk.CTkButton(ventana_simulacion, text="Mostrar grafo y matriz de adyacencia",
                  font=("Montserrat", 20), fg_color="#f7c04a", hover_color="#f9ca5f",
                  text_color="white", width=370, height=60, corner_radius=50,
                  command=mostrar_grafo_y_matriz).place(relx=0.5, rely=0.55, anchor=CENTER)

    ctk.CTkButton(ventana_simulacion, text="Buscar ciclo Hamiltoniano (óptimo)",
                  font=("Montserrat", 20), fg_color="#afde72", hover_color="#a1df5f",
                  text_color="white", width=370, height=60, corner_radius=50,
                  command=mostrar_menor_recorrido).place(relx=0.5, rely=0.70, anchor=CENTER)

    # Botón volver
    ctk.CTkButton(ventana_simulacion, text="Volver al menú principal",
                  font=("Montserrat", 16, "bold"), fg_color="#4b70ff", text_color="white",
                  width=220, height=45, corner_radius=30, command=ventana_simulacion.destroy).place(relx=0.5, rely=0.88, anchor=CENTER)


# ---------------- MENÚ PRINCIPAL ----------------

ctk.CTkLabel(root, text="🧭", font=("Segoe UI Emoji", 36),
             text_color="#815c36").place(relx=0.5, rely=0.10, anchor=CENTER)
ctk.CTkLabel(root, text="PROBLEMA DEL AGENTE VIAJERO",
             font=("Montserrat", 45, "bold"), text_color="#815c36").place(relx=0.5, rely=0.23, anchor=CENTER)

ctk.CTkButton(root, text="Empezar simulación",
              font=("Montserrat", 22), fg_color="#ff4b4b", hover_color="#ff6666",
              text_color="white", width=280, height=60, corner_radius=50,
              command=abrir_simulacion).place(relx=0.5, rely=0.45, anchor=CENTER)

ctk.CTkButton(root, text="Instrucciones",
              font=("Montserrat", 22), fg_color="#afde72", hover_color="#a1df5f",
              text_color="white", width=280, height=60, corner_radius=50,
              command=abrir_instrucciones).place(relx=0.5, rely=0.60, anchor=CENTER)

ctk.CTkButton(root, text="Créditos",
              font=("Montserrat", 22), fg_color="#4b70ff", hover_color="#6688ff",
              text_color="white", width=280, height=60, corner_radius=50,
              command=abrir_creditos).place(relx=0.5, rely=0.75, anchor=CENTER)


# ---------------- INICIO ----------------
root.mainloop()