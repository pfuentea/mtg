# Mejoras Arquitectónicas y de Funcionalidades para la App MTG

Este documento detalla las propuestas arquitectónicas y algorítmicas para implementar los nuevos requerimientos en la plataforma de intercambio y búsqueda de cartas de Magic: The Gathering.

## 1. Privacidad de los Listados y Sistema de Grupos

Actualmente, los listados (`Listados`) pertenecen a un usuario (`owner`). Para soportar múltiples niveles de privacidad y comunidades:

### Modelos de Base de Datos
- **Nuevo Modelo `Grupo`:** Crear el modelo `Grupo` (o `Comunidad`) con campos: `nombre`, `descripcion`, `owner` (ForeignKey a User), y `miembros` (ManyToManyField a User).
- **Modificación a `Listados`:** 
  - Agregar un campo `privacidad` con opciones: `PUBLIC` (Público), `PRIVATE` (Privado), `SHARED` (Compartido a usuarios) y `GROUP` (Compartido a un grupo).
  - Agregar relación `shared_with_users` (M2M hacia `User`).
  - Agregar relación `shared_with_groups` (M2M hacia `Grupo`).

### Interfaz de Usuario (UI)
- **Modal de Creación:** Al crear una nueva lista, en lugar de que aparezca un nuevo `div`, se abrirá un **Modal** flotante. En este modal el usuario ingresará el nombre de la lista, la descripción y seleccionará directamente el nivel de privacidad (y a quién se lo comparte si corresponde).
- **Tabla de Listados:** En la tabla donde aparecen los listados del usuario (`index.html` u `offer/hunt.html`), se agregará una columna o insignia (badge) que muestre visualmente la privacidad de la lista (ej. un ícono de candado para privado, un mundo para público).
- **Menú de Navegación:** Se añadirá una nueva opción en el menú principal o barra lateral llamada "Mis Grupos" o "Comunidades", que llevará a una pantalla donde el usuario podrá crear grupos y agregar usuarios específicos a los mismos.

### Lógica de Vistas (Privacidad Backend)
- Modificar los QuerySets para que devuelvan items solo si `privacidad == 'PUBLIC'`, si el usuario es el `owner`, si el usuario está en `shared_with_users`, o si el usuario pertenece a algún grupo en `shared_with_groups`.

## 2. Atributos de las Cartas (Separación de Conceptos)

En MTG, la entidad `Carta` es global. Los detalles específicos del estado físico pertenecen a la colección particular que tiene el usuario (`ItemLista`).

### Modificaciones
- En `ItemLista`: Agregar `idioma` (EN, ES, JP, etc.), `estado_fisico` (NM, LP, MP, HP, DMG), `es_etched` (booleano), `esta_firmada` (booleano).
- En `Carta`: Agregar el campo `scryfall_id` (UUID) para tener un identificador universal, además de `mana_cost`, `type_line`, `oracle_text`.

## 3. Carga Masiva desde Manabox y Moxfield (con Scryfall)

Crearemos un motor de importación que pueda procesar directamente los archivos CSV de Manabox y Moxfield.

### Módulo de Parsing (`ctm_app/utils/parser.py`)
- **Lazy Loading (Scryfall):** 
  1. Al leer una carta del archivo, el sistema busca en la base de datos local `Carta` por su nombre y código de edición.
  2. Si **no** existe, el backend hace un request a la API de Scryfall (ej. `https://api.scryfall.com/cards/named?exact=[Name]&set=[Set]`).
  3. Se descarga la información de Scryfall, se guarda la nueva carta en la tabla global `Carta`, y finalmente se crea el `ItemLista` del usuario.

## 4. Niveles de Usuarios (Tiers) y Monetización

Para restringir características y generar esquemas de suscripción.

### Modificaciones
- Agregar un nuevo campo `tier` a `User` con opciones: `FREE`, `PRO`, `PREMIUM`.
- Implementar decoradores como `@tier_required('PRO')` para restringir el acceso a la importación masiva y limitar la creación excesiva de grupos.
