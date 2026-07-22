# proyecto-aat

# Forza F1: Dashboard Interactivo y Simulador de Telemetría

## 📌 Descripción del Proyecto
Este proyecto es un **dashboard interactivo de Fórmula 1** desarrollado como aplicación web en Python utilizando **Streamlit**. Nació como un proyecto de aprendizaje paso a paso para centralizar la información técnica, estadística, geográfica y estratégica de la categoría reina del automovilismo en un solo centro de mando visual y moderno (*Pit-Wall Elite & Glassmorphism*).

---

## 🚀 Características Principales
* **Selector de Escuderías y Temporadas (2023 - 2024):** Visualización de datos clave de cada equipo, incluyendo país de origen, unidad de potencia (motor), base de operaciones y estadísticas de efectividad.
* **Batalla Cara a Cara (Head-to-Head):** Comparativa directa de rendimiento, velocidad punta estimada, ritmo de Q3 y puntuación acumulada entre cualquier piloto de la parrilla.
* **Calendario y Geolocalización:** Explorador interactivo de los Grandes Premios con mapas dinámicos de las sedes y fábricas.
* **AWS Insights (Simulador Meteorológico y de Neumáticos):** Simulador atmosférico interactivo que calcula en tiempo real la temperatura del asfalto, el nivel de agarre (*Grip Index*), la tasa de degradación por circuito y la recomendación estratégica de compuestos Pirelli.
* **Clasificaciones Dinámicas:** Tablas editables en tiempo real con actualización automática en gráficas de barras interactivas de Plotly.

---

## 🎮 Instrucciones de Uso

Una vez que tengas la aplicación abierta en tu navegador, podrás navegar a través de sus diferentes pestañas interactivas:

1. **Gestión de Escuderías (Pestaña Principal):**
   * Utiliza el selector superior para alternar entre las temporadas **2023** y **2024**.
   * Selecciona una escudería en el menú desplegable para actualizar instantáneamente las tarjetas de rendimiento (KPIs), los logotipos oficiales, la alineación de pilotos y la ubicación de su fábrica en el mapa.
   * Modifica los valores numéricos directamente en la tabla interactiva de puntos para ver cómo la gráfica de barras de Plotly se actualiza en tiempo real.

2. **Batalla Cara a Cara - H2H (Pestaña 2):**
   * Selecciona al **Piloto A** y al **Piloto B** en los selectores enfrentados.
   * Analiza las tarjetas comparativas de velocidad punta, ritmo de Q3 y puntos acumulados, junto con la gráfica de barras agrupadas y el veredicto automático de la temporada.

3. **Calendario y Mapas (Pestaña 3):**
   * Elige cualquier Gran Premio del calendario para consultar los detalles técnicos del circuito, fecha formateada, ganador y su geolocalización exacta en el mapa.
   * Utiliza el filtro de ganadores para consultar de forma rápida cuántas victorias obtuvo un piloto específico en la temporada.

4. **Simulador AWS Insights - Clima y Neumáticos (Pestaña 5):**
   * Selecciona un circuito del campeonato para aplicar su **factor de abrasión** específico.
   * Ajusta los controles deslizantes (*sliders*) de **Temperatura Ambiente**, **Probabilidad de Lluvia**, **Humedad** y **Viento**.
   * Observa cómo los indicadores visuales (*gauges*) calculan el **Nivel de Agarre (Grip Index)** y la **Temperatura del Asfalto**.
   * Revisa la recomendación estratégica de compuestos Pirelli (Blandos, Medios, Duros, Intermedios o de Lluvia Extrema) junto con la tasa de desgaste por vuelta y la vida útil estimada.

---

## 🛠️ Stack Tecnológico
* **Python:** Lenguaje principal de programación y lógica de backend.
* **Streamlit:** Framework para la construcción de la interfaz web interactiva.
* **Pandas y NumPy:** Manipulación y procesamiento de estructuras de datos tabulares.
* **Plotly (Express / Graph Objects):** Generación de gráficas de alto rendimiento y medidores dinámicos (*gauges*).
* **Geopy:** Resolución de coordenadas geográficas para los mapas de sedes.

---

## 📦 Instalación y Ejecución Local

Si deseas clonar y ejecutar este proyecto en tu propia máquina, sigue estos pasos:

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repositorio.git](https://github.com/tu-usuario/nombre-del-repositorio.git)
   cd nombre-del-repositorio
