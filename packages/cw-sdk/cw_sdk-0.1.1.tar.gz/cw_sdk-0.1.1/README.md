# 📘 Explicación interna de la clase `SharePointGraph`

Este archivo documenta cómo está construida y cómo funciona internamente la clase `SharePointGraph`, diseñada para interactuar con SharePoint Online mediante Microsoft Graph API.

---

## 📦 Objetivo general

Automatizar operaciones con archivos y carpetas dentro de SharePoint (lectura, escritura, verificación, eliminación) a través de HTTP puro (`http.client`) sin usar SDKs externos de Microsoft.

---

## 🧱 Atributos de instancia (`__init__`)

```python
def __init__(self):
    self.SECRETID = None
    self.APPID = None
    self.TENANTID = None
    self.token = None
    self.site_id = None
    self.drive_id = None
    self.item_id = None
```

- Guarda las credenciales y recursos necesarios para las operaciones.
- Se inician en `None` y se completan dinámicamente tras autenticarse o navegar por SharePoint.

---

## 🔐 Autenticación

### `_az_auth(secret_id, app_id, tenant_id)`

Guarda las credenciales necesarias para autenticarse.

---

### `get_token()`

Autentica contra Azure AD usando MSAL (`ConfidentialClientApplication`) y guarda el token de acceso (`self.token`).

- Se utiliza el flujo *client credentials*.
- Scope usado: `https://graph.microsoft.com/.default`.

---

## 🌍 Identificación de recursos

### `get_site_id(context)`

- Toma el nombre del sitio desde la variable de entorno:
  - `sharepoint_site_name` para `cw`
  - `sharepoint_site_name_legales` para `legales`
- Consulta la API `/v1.0/sites/...` para obtener el `site_id`.
- Lo guarda en `self.site_id`.

---

### `get_drive_id(context)`

- Usa `site_id` para obtener los drives disponibles con:
  - `/v1.0/sites/{site_id}/drives`
- Selecciona el tercer drive (`value[2]`) y guarda su ID.

---

### `get_item_id(base_path, context)`

- Navega al path dado (`base_path`) y busca por nombre el ítem que coincide con la última carpeta del path.
- Guarda su ID como `self.item_id`.
- Se usa para subir nuevos archivos.

---

## 🔁 Flujo compuesto

### `_auth(base_path, context)`

Método interno que corre en orden:

1. `get_token()`
2. `get_site_id()`
3. `get_drive_id()`
4. `get_item_id(base_path)`

Se asegura de que todos los datos necesarios estén disponibles para las operaciones siguientes.

---

## 📁 Manejo de carpetas

### `check_dir(folder_name, base_path, context)`

- Verifica si una carpeta existe dentro del `base_path`.
- Itera por las páginas del endpoint `/children`.
- Compara nombres con `folder_name` (ignorando mayúsculas/minúsculas).

---

### `mk_dir(folder_name, base_path, context)`

- Crea una nueva carpeta dentro del ítem identificado por `base_path`.
- Usa el endpoint `/items/{item_id}/children` con `POST`.
- Si la carpeta ya existe, SharePoint renombra automáticamente.

---

## 📄 Manejo de archivos

### `upload_file(base_path, file_name, content_bytes, context)`

- Sube un archivo como binario (`PUT`) al path indicado.
- Usa el endpoint `/root:/{path}/{file}:/content`
- Si el archivo ya existe, lo sobreescribe o renombra según conflicto.

---

### `download_file(base_path, file_name, context)`

- Descarga un archivo como bytes desde SharePoint.
- Endpoint: `/root:/{path}/{file}:/content`
- Retorna los bytes, que pueden ser guardados en disco.

---

### `del_file(filename, base_path, context)`

- Navega el árbol `"Datos/ADUANAS/Robot"` y sus subdirectorios.
- Elimina todos los archivos cuyo nombre contiene el string `filename`.
- Usa `DELETE` contra `/items/{file_id}`.

---

## 🧪 Notas técnicas

- Usa `http.client` para controlar manualmente las solicitudes HTTP.
- No depende de `requests` ni SDKs de Microsoft.
- Usa paginación con `@odata.nextLink` para explorar listas largas.

---

## 🔐 Variables de entorno requeridas

```env
sharepoint_site_name=nombre_del_sitio_para_contexto_cw
sharepoint_site_name_legales=nombre_para_contexto_legales
```

---

## 🛠️ Recomendaciones

- Se recomienda encapsular el manejo de logs y errores a nivel de integración.
- El método `_auth()` puede ser llamado automáticamente por los métodos públicos si no hay estado.

---

## 📄 Última actualización

Generado automáticamente para documentación interna del proyecto Customs Watch.

