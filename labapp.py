import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Sistema de Equipos de Laboratorio",
    page_icon="💻",
    layout="wide"
)


# =========================================================
# CONEXIÓN A SUPABASE
# =========================================================
@st.cache_resource
def conectar_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


supabase: Client = conectar_supabase()


# =========================================================
# ESTILOS
# =========================================================
st.markdown("""
<style>

.titulo-principal {
    font-size: 38px;
    font-weight: bold;
    margin-bottom: 5px;
}

.subtitulo {
    font-size: 17px;
    color: gray;
    margin-bottom: 25px;
}

div[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,0.25);
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stForm"] {
    border: 1px solid rgba(128,128,128,0.25);
    padding: 20px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCIONES PARA OBTENER DATOS
# =========================================================
def obtener_equipos():
    try:
        respuesta = (
            supabase
            .table("EQUIPOS LAB")
            .select("*")
            .order("codigo")
            .execute()
        )

        return respuesta.data

    except Exception as e:
        st.error(f"Error al obtener equipos: {e}")
        return []


def obtener_marcas():
    try:
        respuesta = (
            supabase
            .table("marcas")
            .select("*")
            .order("codigo_marca")
            .execute()
        )

        return respuesta.data

    except Exception as e:
        st.error(f"Error al obtener marcas: {e}")
        return []


def obtener_responsables():
    try:
        respuesta = (
            supabase
            .table("responsables")
            .select("*")
            .order("codigo_responsable")
            .execute()
        )

        return respuesta.data

    except Exception as e:
        st.error(f"Error al obtener responsables: {e}")
        return []


# =========================================================
# GENERAR CÓDIGO AUTOMÁTICO
# =========================================================
def generar_codigo_equipo(lista_equipos):

    if not lista_equipos:
        return "EQ001"

    numeros = []

    for equipo in lista_equipos:

        codigo = equipo.get("codigo", "")

        if codigo.startswith("EQ"):

            try:
                numero = int(codigo.replace("EQ", ""))
                numeros.append(numero)

            except:
                pass

    if not numeros:
        return "EQ001"

    siguiente = max(numeros) + 1

    return f"EQ{siguiente:03d}"


# =========================================================
# FUNCIÓN PARA CONVERTIR FECHAS
# =========================================================
def fecha_segura(valor):

    if not valor:
        return date.today()

    try:
        return pd.to_datetime(valor).date()

    except:
        return date.today()


# =========================================================
# CARGAR DATOS
# =========================================================
equipos = obtener_equipos()
marcas = obtener_marcas()
responsables = obtener_responsables()


dic_marcas = {
    item["codigo_marca"]: item["marca"]
    for item in marcas
}


dic_responsables = {
    item["codigo_responsable"]: item["responsable"]
    for item in responsables
}


# =========================================================
# MENÚ LATERAL
# =========================================================
st.sidebar.title("💻 EQUIPO LAB")

st.sidebar.write(
    "Sistema de gestión de equipos del laboratorio"
)

st.sidebar.divider()


menu = st.sidebar.radio(
    "Menú principal",
    [
        "🏠 Dashboard",
        "💻 Equipos",
        "🏷️ Marcas",
        "👤 Responsables"
    ]
)


st.sidebar.divider()

st.sidebar.success("✅ Conectado a Supabase")


# =========================================================
# DASHBOARD
# =========================================================
if menu == "🏠 Dashboard":

    st.markdown(
        '<div class="titulo-principal">🏠 Panel principal</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">Resumen general del laboratorio</div>',
        unsafe_allow_html=True
    )


    total_registros = len(equipos)

    total_cantidad = sum(
        int(e.get("cantidad", 0))
        for e in equipos
    )


    operativos = sum(
        1 for e in equipos
        if e.get("estado") == "Operativo"
    )


    mantenimiento = sum(
        1 for e in equipos
        if e.get("estado") == "Mantenimiento"
    )


    inoperativos = sum(
        1 for e in equipos
        if e.get("estado") == "Inoperativo"
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "💻 Registros",
        total_registros
    )


    col2.metric(
        "📦 Cantidad total",
        total_cantidad
    )


    col3.metric(
        "✅ Operativos",
        operativos
    )


    col4.metric(
        "🔧 Mantenimiento",
        mantenimiento
    )


    st.divider()


    col1, col2 = st.columns(2)


    with col1:

        st.subheader("📊 Estado de equipos")

        datos_estado = pd.DataFrame({

            "Estado": [
                "Operativo",
                "Mantenimiento",
                "Inoperativo"
            ],

            "Cantidad": [
                operativos,
                mantenimiento,
                inoperativos
            ]

        })

        st.bar_chart(
            datos_estado.set_index("Estado")
        )


    with col2:

        st.subheader("📋 Información general")

        st.info(
            f"""
            **Registros de equipos:** {total_registros}

            **Marcas registradas:** {len(marcas)}

            **Responsables registrados:** {len(responsables)}

            **Cantidad total de equipos:** {total_cantidad}
            """
        )


# =========================================================
# EQUIPOS
# =========================================================
elif menu == "💻 Equipos":

    st.markdown(
        '<div class="titulo-principal">💻 Gestión de Equipos</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">Registro, consulta, actualización y eliminación de equipos</div>',
        unsafe_allow_html=True
    )


    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ver equipos",
        "➕ Registrar",
        "✏️ Actualizar",
        "🗑️ Eliminar"
    ])


    # =====================================================
    # VER EQUIPOS
    # =====================================================
    with tab1:

        st.subheader("📋 Lista de equipos")


        if equipos:

            df = pd.DataFrame(equipos)


            # Mostrar nombres
            df["nombre_marca"] = (
                df["marca"]
                .map(dic_marcas)
                .fillna(df["marca"])
            )


            df["nombre_responsable"] = (
                df["responsable"]
                .map(dic_responsables)
                .fillna(df["responsable"])
            )


            st.markdown("### 🔎 Filtros")


            col1, col2, col3, col4 = st.columns(4)


            with col1:

                buscar = st.text_input(
                    "Buscar",
                    placeholder="Código o descripción..."
                )


            with col2:

                filtro_marca = st.selectbox(
                    "Marca",
                    ["Todas"] + list(dic_marcas.keys()),
                    format_func=lambda x:
                    "Todas las marcas"
                    if x == "Todas"
                    else f"{x} - {dic_marcas[x]}"
                )


            with col3:

                filtro_responsable = st.selectbox(
                    "Responsable",
                    ["Todos"] + list(dic_responsables.keys()),
                    format_func=lambda x:
                    "Todos los responsables"
                    if x == "Todos"
                    else f"{x} - {dic_responsables[x]}"
                )


            with col4:

                filtro_estado = st.selectbox(
                    "Estado",
                    [
                        "Todos",
                        "Operativo",
                        "Mantenimiento",
                        "Inoperativo"
                    ]
                )


            # -----------------------------
            # FILTRO POR TEXTO
            # -----------------------------
            if buscar:

                buscar = buscar.lower()

                df = df[
                    df.astype(str)
                    .apply(
                        lambda fila:
                        fila.str.lower()
                        .str.contains(
                            buscar,
                            na=False
                        )
                        .any(),
                        axis=1
                    )
                ]


            # -----------------------------
            # FILTRO POR MARCA
            # -----------------------------
            if filtro_marca != "Todas":

                df = df[
                    df["marca"] == filtro_marca
                ]


            # -----------------------------
            # FILTRO POR RESPONSABLE
            # -----------------------------
            if filtro_responsable != "Todos":

                df = df[
                    df["responsable"]
                    == filtro_responsable
                ]


            # -----------------------------
            # FILTRO POR ESTADO
            # -----------------------------
            if filtro_estado != "Todos":

                df = df[
                    df["estado"]
                    == filtro_estado
                ]


            st.write(
                f"**Resultados encontrados:** {len(df)}"
            )


            columnas = [

                "codigo",
                "descripcion",
                "nombre_marca",
                "estado",
                "fecha_adquisicion",
                "fecha_ult_mant",
                "fecha_prox_mant",
                "nombre_responsable",
                "cantidad"

            ]


            df_mostrar = df[columnas].copy()


            df_mostrar.columns = [

                "Código",
                "Descripción",
                "Marca",
                "Estado",
                "Fecha adquisición",
                "Último mantenimiento",
                "Próximo mantenimiento",
                "Responsable",
                "Cantidad"

            ]


            st.dataframe(
                df_mostrar,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "No existen equipos registrados."
            )


    # =====================================================
    # REGISTRAR EQUIPO
    # =====================================================
    with tab2:

        st.subheader("➕ Registrar nuevo equipo")


        if not marcas:

            st.warning(
                "Primero debes registrar una marca."
            )


        elif not responsables:

            st.warning(
                "Primero debes registrar un responsable."
            )


        else:

            nuevo_codigo = generar_codigo_equipo(
                equipos
            )


            st.info(
                f"🔢 El código será generado automáticamente: "
                f"**{nuevo_codigo}**"
            )


            st.info(
                "🛠️ El mantenimiento preventivo está programado "
                "cada **12 meses**. La fecha del próximo mantenimiento "
                "se calculará automáticamente a partir de la fecha "
                "del último mantenimiento."
            )


            with st.form(
                "form_registrar_equipo",
                clear_on_submit=True
            ):


                col1, col2 = st.columns(2)


                with col1:

                    st.text_input(
                        "Código",
                        value=nuevo_codigo,
                        disabled=True
                    )


                    descripcion = st.text_input(
                        "Descripción",
                        placeholder="Ejemplo: Laptop para laboratorio"
                    )


                    marca = st.selectbox(
                        "Marca",
                        list(dic_marcas.keys()),
                        format_func=lambda x:
                        f"{x} - {dic_marcas[x]}"
                    )


                    estado = st.selectbox(
                        "Estado",
                        [
                            "Operativo",
                            "Mantenimiento",
                            "Inoperativo"
                        ]
                    )


                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=1,
                        value=1,
                        step=1
                    )


                with col2:

                    responsable = st.selectbox(
                        "Responsable",
                        list(dic_responsables.keys()),
                        format_func=lambda x:
                        f"{x} - {dic_responsables[x]}"
                    )


                    fecha_adquisicion = st.date_input(
                        "Fecha de adquisición",
                        value=date.today()
                    )


                    fecha_ult_mant = st.date_input(
                        "Fecha del último mantenimiento",
                        value=date.today()
                    )


                    # CALCULAR AUTOMÁTICAMENTE
                    fecha_prox_mant = (
                        fecha_ult_mant
                        + relativedelta(months=12)
                    )


                    st.date_input(
                        "Fecha del próximo mantenimiento",
                        value=fecha_prox_mant,
                        disabled=True
                    )


                guardar = st.form_submit_button(
                    "💾 Registrar equipo",
                    use_container_width=True
                )


                if guardar:

                    if descripcion.strip() == "":

                        st.warning(
                            "Ingrese una descripción."
                        )

                    else:

                        try:

                            # Se genera nuevamente antes de insertar
                            # para evitar códigos repetidos
                            codigo_final = generar_codigo_equipo(
                                obtener_equipos()
                            )


                            fecha_prox_final = (
                                fecha_ult_mant
                                + relativedelta(months=12)
                            )


                            datos = {

                                "codigo":
                                    codigo_final,

                                "descripcion":
                                    descripcion.strip(),

                                "marca":
                                    marca,

                                "estado":
                                    estado,

                                "fecha_adquisicion":
                                    fecha_adquisicion.isoformat(),

                                "fecha_ult_mant":
                                    fecha_ult_mant.isoformat(),

                                "fecha_prox_mant":
                                    fecha_prox_final.isoformat(),

                                "responsable":
                                    responsable,

                                "cantidad":
                                    cantidad
                            }


                            (
                                supabase
                                .table("EQUIPOS LAB")
                                .insert(datos)
                                .execute()
                            )


                            st.success(
                                f"✅ Equipo {codigo_final} "
                                f"registrado correctamente."
                            )


                            st.rerun()


                        except Exception as e:

                            st.error(
                                f"Error al registrar: {e}"
                            )


    # =====================================================
    # ACTUALIZAR EQUIPO
    # =====================================================
    with tab3:

        st.subheader("✏️ Actualizar equipo")


        if equipos:

            opciones_equipos = [
                e["codigo"]
                for e in equipos
            ]


            codigo_seleccionado = st.selectbox(
                "Seleccionar equipo",
                opciones_equipos,
                key="editar_equipo"
            )


            equipo = next(
                (
                    e for e in equipos
                    if e["codigo"]
                    == codigo_seleccionado
                ),
                None
            )


            if equipo:

                st.info(
                    "🛠️ El próximo mantenimiento se calcula "
                    "automáticamente **12 meses después** "
                    "del último mantenimiento."
                )


                with st.form(
                    "form_actualizar_equipo"
                ):


                    col1, col2 = st.columns(2)


                    with col1:

                        st.text_input(
                            "Código",
                            value=codigo_seleccionado,
                            disabled=True
                        )


                        descripcion_edit = st.text_input(
                            "Descripción",
                            value=equipo.get(
                                "descripcion",
                                ""
                            )
                        )


                        lista_marcas = list(
                            dic_marcas.keys()
                        )


                        marca_actual = equipo.get(
                            "marca"
                        )


                        indice_marca = (
                            lista_marcas.index(
                                marca_actual
                            )
                            if marca_actual
                            in lista_marcas
                            else 0
                        )


                        marca_edit = st.selectbox(
                            "Marca",
                            lista_marcas,
                            index=indice_marca,
                            format_func=lambda x:
                            f"{x} - {dic_marcas[x]}"
                        )


                        estados = [
                            "Operativo",
                            "Mantenimiento",
                            "Inoperativo"
                        ]


                        estado_actual = equipo.get(
                            "estado",
                            "Operativo"
                        )


                        indice_estado = (
                            estados.index(
                                estado_actual
                            )
                            if estado_actual
                            in estados
                            else 0
                        )


                        estado_edit = st.selectbox(
                            "Estado",
                            estados,
                            index=indice_estado
                        )


                        cantidad_edit = st.number_input(
                            "Cantidad",
                            min_value=1,
                            value=int(
                                equipo.get(
                                    "cantidad",
                                    1
                                )
                            ),
                            step=1
                        )


                    with col2:

                        lista_resp = list(
                            dic_responsables.keys()
                        )


                        responsable_actual = (
                            equipo.get(
                                "responsable"
                            )
                        )


                        indice_resp = (
                            lista_resp.index(
                                responsable_actual
                            )
                            if responsable_actual
                            in lista_resp
                            else 0
                        )


                        responsable_edit = st.selectbox(
                            "Responsable",
                            lista_resp,
                            index=indice_resp,
                            format_func=lambda x:
                            f"{x} - {dic_responsables[x]}"
                        )


                        fecha_adq = st.date_input(
                            "Fecha de adquisición",
                            value=fecha_segura(
                                equipo.get(
                                    "fecha_adquisicion"
                                )
                            )
                        )


                        fecha_ult = st.date_input(
                            "Último mantenimiento",
                            value=fecha_segura(
                                equipo.get(
                                    "fecha_ult_mant"
                                )
                            )
                        )


                        fecha_prox = (
                            fecha_ult
                            + relativedelta(months=12)
                        )


                        st.date_input(
                            "Próximo mantenimiento",
                            value=fecha_prox,
                            disabled=True
                        )


                    guardar_cambios = (
                        st.form_submit_button(
                            "💾 Guardar cambios",
                            use_container_width=True
                        )
                    )


                    if guardar_cambios:

                        try:

                            datos = {

                                "descripcion":
                                    descripcion_edit.strip(),

                                "marca":
                                    marca_edit,

                                "estado":
                                    estado_edit,

                                "fecha_adquisicion":
                                    fecha_adq.isoformat(),

                                "fecha_ult_mant":
                                    fecha_ult.isoformat(),

                                "fecha_prox_mant":
                                    fecha_prox.isoformat(),

                                "responsable":
                                    responsable_edit,

                                "cantidad":
                                    cantidad_edit
                            }


                            (
                                supabase
                                .table("EQUIPOS LAB")
                                .update(datos)
                                .eq(
                                    "codigo",
                                    codigo_seleccionado
                                )
                                .execute()
                            )


                            st.success(
                                "✅ Equipo actualizado."
                            )


                            st.rerun()


                        except Exception as e:

                            st.error(
                                f"Error: {e}"
                            )


        else:

            st.info(
                "No existen equipos registrados."
            )


    # =====================================================
    # ELIMINAR
    # =====================================================
    with tab4:

        st.subheader("🗑️ Eliminar equipo")


        if equipos:

            codigo_eliminar = st.selectbox(
                "Seleccionar equipo",
                [
                    e["codigo"]
                    for e in equipos
                ],
                key="eliminar_equipo"
            )


            equipo = next(
                e for e in equipos
                if e["codigo"] == codigo_eliminar
            )


            marca_nombre = dic_marcas.get(
                equipo.get("marca"),
                equipo.get("marca")
            )


            responsable_nombre = (
                dic_responsables.get(
                    equipo.get("responsable"),
                    equipo.get("responsable")
                )
            )


            st.warning(
                f"""
                Estás a punto de eliminar:

                **Código:** {equipo["codigo"]}

                **Descripción:** {equipo["descripcion"]}

                **Marca:** {marca_nombre}

                **Responsable:** {responsable_nombre}
                """
            )


            confirmar = st.checkbox(
                "Confirmo que deseo eliminar este equipo"
            )


            if st.button(
                "🗑️ Eliminar equipo",
                disabled=not confirmar,
                type="primary",
                use_container_width=True
            ):

                try:

                    (
                        supabase
                        .table("EQUIPOS LAB")
                        .delete()
                        .eq(
                            "codigo",
                            codigo_eliminar
                        )
                        .execute()
                    )


                    st.success(
                        "✅ Equipo eliminado."
                    )


                    st.rerun()


                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )


# =========================================================
# MARCAS
# =========================================================
elif menu == "🏷️ Marcas":

    st.markdown(
        '<div class="titulo-principal">🏷️ Gestión de Marcas</div>',
        unsafe_allow_html=True
    )


    tab1, tab2, tab3 = st.tabs([
        "📋 Ver marcas",
        "➕ Agregar",
        "🗑️ Eliminar"
    ])


    with tab1:

        st.subheader("📋 Marcas registradas")


        if marcas:

            df_marcas = pd.DataFrame(marcas)

            df_marcas.columns = [
                "Código",
                "Marca"
            ]


            st.dataframe(
                df_marcas,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "No existen marcas registradas."
            )


    with tab2:

        st.subheader("➕ Registrar nueva marca")


        with st.form(
            "form_marca",
            clear_on_submit=True
        ):

            codigo_marca = st.text_input(
                "Código",
                placeholder="Ejemplo: M05"
            )


            nombre_marca = st.text_input(
                "Marca",
                placeholder="Ejemplo: Acer"
            )


            agregar = st.form_submit_button(
                "💾 Guardar marca",
                use_container_width=True
            )


            if agregar:

                if not codigo_marca.strip():

                    st.warning(
                        "Ingrese el código."
                    )


                elif not nombre_marca.strip():

                    st.warning(
                        "Ingrese el nombre de la marca."
                    )


                else:

                    try:

                        datos = {

                            "codigo_marca":
                                codigo_marca.upper().strip(),

                            "marca":
                                nombre_marca.strip()
                        }


                        (
                            supabase
                            .table("marcas")
                            .insert(datos)
                            .execute()
                        )


                        st.success(
                            "✅ Marca registrada."
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


    with tab3:

        st.subheader("🗑️ Eliminar marca")


        if marcas:

            marca_eliminar = st.selectbox(
                "Seleccionar marca",
                list(dic_marcas.keys()),
                format_func=lambda x:
                f"{x} - {dic_marcas[x]}"
            )


            uso_marca = [
                e for e in equipos
                if e.get("marca")
                == marca_eliminar
            ]


            if uso_marca:

                st.warning(
                    f"Esta marca está siendo utilizada por "
                    f"{len(uso_marca)} registro(s) de equipos."
                )


            confirmar = st.checkbox(
                "Confirmo eliminar la marca",
                key="confirmar_marca"
            )


            if st.button(
                "🗑️ Eliminar marca",
                disabled=not confirmar,
                key="btn_eliminar_marca"
            ):

                if uso_marca:

                    st.error(
                        "No puedes eliminar esta marca porque "
                        "está siendo utilizada por equipos."
                    )


                else:

                    try:

                        (
                            supabase
                            .table("marcas")
                            .delete()
                            .eq(
                                "codigo_marca",
                                marca_eliminar
                            )
                            .execute()
                        )


                        st.success(
                            "✅ Marca eliminada."
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


# =========================================================
# RESPONSABLES
# =========================================================
elif menu == "👤 Responsables":

    st.markdown(
        '<div class="titulo-principal">👤 Gestión de Responsables</div>',
        unsafe_allow_html=True
    )


    tab1, tab2, tab3 = st.tabs([
        "📋 Ver responsables",
        "➕ Agregar",
        "🗑️ Eliminar"
    ])


    with tab1:

        st.subheader(
            "📋 Responsables registrados"
        )


        if responsables:

            df_resp = pd.DataFrame(responsables)

            df_resp.columns = [
                "Código",
                "Responsable"
            ]


            st.dataframe(
                df_resp,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "No existen responsables registrados."
            )


    with tab2:

        st.subheader(
            "➕ Registrar responsable"
        )


        with st.form(
            "form_responsable",
            clear_on_submit=True
        ):

            codigo_responsable = st.text_input(
                "Código",
                placeholder="Ejemplo: R05"
            )


            nombre_responsable = st.text_input(
                "Nombre del responsable",
                placeholder="Ejemplo: Pedro Arévalo"
            )


            guardar = st.form_submit_button(
                "💾 Guardar responsable",
                use_container_width=True
            )


            if guardar:

                if not codigo_responsable.strip():

                    st.warning(
                        "Ingrese el código."
                    )


                elif not nombre_responsable.strip():

                    st.warning(
                        "Ingrese el nombre."
                    )


                else:

                    try:

                        datos = {

                            "codigo_responsable":
                                codigo_responsable.upper().strip(),

                            "responsable":
                                nombre_responsable.strip()
                        }


                        (
                            supabase
                            .table("responsables")
                            .insert(datos)
                            .execute()
                        )


                        st.success(
                            "✅ Responsable registrado."
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


    with tab3:

        st.subheader(
            "🗑️ Eliminar responsable"
        )


        if responsables:

            responsable_eliminar = (
                st.selectbox(
                    "Seleccionar responsable",
                    list(
                        dic_responsables.keys()
                    ),
                    format_func=lambda x:
                    f"{x} - "
                    f"{dic_responsables[x]}"
                )
            )


            uso_responsable = [
                e for e in equipos
                if e.get("responsable")
                == responsable_eliminar
            ]


            if uso_responsable:

                st.warning(
                    f"Este responsable está asignado a "
                    f"{len(uso_responsable)} registro(s) "
                    f"de equipos."
                )


            confirmar = st.checkbox(
                "Confirmo eliminar el responsable",
                key="confirmar_resp"
            )


            if st.button(
                "🗑️ Eliminar responsable",
                disabled=not confirmar,
                key="btn_eliminar_resp"
            ):

                if uso_responsable:

                    st.error(
                        "No puedes eliminar este responsable "
                        "porque está asignado a equipos."
                    )


                else:

                    try:

                        (
                            supabase
                            .table("responsables")
                            .delete()
                            .eq(
                                "codigo_responsable",
                                responsable_eliminar
                            )
                            .execute()
                        )


                        st.success(
                            "✅ Responsable eliminado."
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )
