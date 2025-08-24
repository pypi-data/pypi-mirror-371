# Paquetes de Zibanu para Django


Zibanu para Django está conformado por los siguientes paquetes: 

- [Paquete de API de Zibanu para Django (zibanu.django.api package)](#paquete-de-api-de-zibanu-para-django-zibanudjangoapi-package)

- [Paquete de Base de Datos de Zibanu para Django (zibanu.django.db package)](#paquete-de-base-de-datos-de-zibanu-para-django-zibanudjangodb-package)

- [Paquete de Marco de Trabajo REST de Zibanu para Django (zibanu.django.rest_framework package)](#paquete-de-marco-de-trabajo-rest-de-zibanu-para-django-zibanudjangorest_framework-package)

- [Paquete de Plantillas de Zibanu para Django (zibanu.django.template package)](#paquete-de-plantillas-de-zibanu-para-django-zibanudjangotemplate-package)

- [Paquete de Utilidades de Zibanu para Django (zibanu.django.utils package)](#paquete-de-utilidades-de-zibanu-para-django-zibanudjangoutils-package)









## Paquete de API de Zibanu para Django (zibanu.django.api package)

Este paquete Django proporciona servicios REST para enumerar los idiomas y zonas horarias disponibles.


### zibanu.django.api.services.language module

Este módulo Django proporciona una API REST para enumerar los idiomas disponibles en un proyecto Django.

```
classzibanu.django.api.services.language.LanguageViewSet(ViewSet)
```
Vista configurada para exponer los servicios REST para enumerar los idiomas disponibles de Django.

**Métodos**

```
list(request, *args, **kwargs)→ Response:
```

Servicio REST para enumerar los idiomas disponibles de Django desde la configuración.

Parámetros:

- ```request:``` Objeto de solicitud HTTP.
- ```*args*:``` Tupla con parámetros.
- ```**kwargs**:``` Diccionario con parámetros clave/valor.


Retorna:

- ```languages:``` Lista con idiomas Django desde la configuración.


### zibanu.django.api.services.timezone module

Este Django ViewSet expone una lista de todas las zonas horarias disponibles.

```
classzibanu.django.api.services.timezone.TimeZoneViewSet(ViewSet)
```
Vista configurada para exponer la lista disponible de zonas horarias.

**Métodos**

```
list(request)→ Response:
```

Listar zonas horarias disponibles.

Parámetros:

- ```request:``` Objeto de solicitud HTTP.

Retorna:

- ```response:``` Objeto de respuesta con estado y lista de zonas horarias.

    Estado -> **200** si la longitud de la lista de zonas horarias > 0, en caso contrario **204**.






______________



## Paquete de Base de Datos de Zibanu para Django (zibanu.django.db package)

Este paquete demuestra el uso de un contenedor de base de datos personalizado y una clase de operaciones para permitir el uso de campos con nombres entre comillas dobles, como palabras reservadas, por ejemplo. También incluye una clase de modelo personalizado que agrega los campos created_at  y modified_at  de forma predeterminada, y una clase de administrador personalizado que incluye el uso del atributo "use_db" de la clase de modelo, si existe.

## zibanu.django.db.backends.oracle package

Esta es una versión modificada del contenedor de base de datos Django.

### zibanu.django.db.backends.oracle.base module

```
classzibanu.django.db.backends.oracle.base.DatabaseOperations(OracleOperations)
```

Clase para anular la clase DatabaseOperation del cliente django Oracle.
Esta clase permite el uso de campos con nombres entre '""', como palabras reservadas por ejemplo.
_____

**Métodos**

```
quote_name(name)→ 
```
Anular método para obtener el nombre del campo respetando las comillas dobles.

Parámetros:

- ```name:``` Nombre del campo de la tabla.

Retorna:

- ```name:``` Nombre del campo con comillas dobles si corresponde.

_____
```
classzibanu.django.db.backends.oracle.base.DatabaseWrapper(OracleWrapper)
```
Clase contenedora de base de datos para usar una nueva clase DatabaseOperation.

## zibanu.django.db.models package

Este paquete contiene un conjunto de modelos abstractos que pueden usarse como base para sus propios modelos de Django.

### zibanu.django.db.models.dated_model module

```
classzibanu.django.db.models.dated_model.DatedModel(*args, **kwargs)
```

Clase abstracta heredada de la clase zibanu.django.db.Model para agregar los campos creado_at y modificado_at de forma predeterminada.______

### zibanu.django.db.models.manager module

```
classzibanu.django.db.models.manager.Manager(*args, **kwargs)
```

Esta es una clase de administrador personalizada para modelos Django. Incluye algunos métodos de utilidad que se pueden utilizar para simplificar tareas comunes.

___________________

**Métodos**

```
get_queryset()→ QuerySet
```

Devuelve un conjunto de consultas para el modelo. Este método se anula para incluir el uso del atributo `use_db` de la clase de modelo, si existe.

Retorna:

- ```qs:``` Objeto de conjunto de consultas.

___________________



```
get_by_pk(pk: Any)→ QuerySet
```

Devuelve un conjunto de consultas para el modelo basado en el campo de clave principal. Este método valida que la clave principal exista antes de devolver el conjunto de consultas.

Parámetros:

- ```pk:``` Valor del campo PK.

Retorna:

- ```qs:``` Objeto de conjunto de consultas.

_____________________

### zibanu.django.db.models.model module

```
classzibanu.django.db.models.model.Model(*args, **kwargs)
```

Esta es una clase base para modelos de Django que agrega el atributo `use_db`. Este atributo le permite especificar qué base de datos usar para un modelo en particular.
_____________________

**Métodos**


```
set(self, fields: dict):
```

Método para guardar un conjunto de campos de un diccionario.

Parámetros:

- *fields:* Diccionario con claves y valores de campos.

Retorna:

- Ninguno.


_____________________







## Paquete de Marco de Trabajo REST de Zibanu para Django (zibanu.django.rest_framework package)

Este paquete contiene extensiones personalizadas para el marco REST de Django.

### zibanu.django.rest_framework.decorators module

```
permission_required(permissions: Any, raise_exception=True)→ 
```

Decorador para validar permisos de la estructura de autenticación de Django. Compatible con JWT simple.

Parámetros:

- ```permissions:``` Nombre de permiso o tupla con lista de permisos. Obligatorio.

- ```raise_exception:``` Verdadero si desea generar la excepción PermissionDenied; de lo contrario, Falso. Valor predeterminado: Verdadero


Retorna:

- ```b_return:``` Verdadero si la autorización se realizó correctamente; en caso contrario, Falso.

___

```
check_perms(user)→ 
```

Función interna para verificar el permiso de la función maestra.


Parámetros:

- ```user:``` Objeto de usuario a validar.


Retorna:

- ```b_return:``` Verdadero si los permisos verifican el éxito; en caso contrario, Falso.



## zibanu.django.rest_framework.exceptions package

Este paquete contiene clases de excepción personalizadas para Django REST Framework.

### zibanu.django.rest_framework.exceptions.api_exception module

```
exceptionzibanu.django.rest_framework.exceptions.api_exception.APIException(msg: str | None = None, error: str | None = None, http_status: int = 400)
```

Clase heredada de rest_framework.exceptions. ApiException.
___

### Contenido del módulo

```
exceptionzibanu.django.rest_framework.exceptions.AuthenticationFailed(detail=None, code=None)
```

```default_code= 'authentication_failed'```

```default_detail```

```status_code= 401```

___

```
exceptionzibanu.django.rest_framework.exceptions.MethodNotAllowed(method, detail=None, code=None)
```

```default_code= 'method_not_allowed'```

```default_detail```

```status_code= 405```

___

```
exceptionzibanu.django.rest_framework.exceptions.NotAcceptable(detail=None, code=None, available_renderers=None)
```

```default_code= 'not_acceptable'```

```default_detail```

```status_code= 406```

___

```
exceptionzibanu.django.rest_framework.exceptions.NotFound(detail=None, code=None)
```

```default_code= 'not_found'```

```default_detail```

```status_code= 404```
___

```
exceptionzibanu.django.rest_framework.exceptions.ParseError(detail=None, code=None)
```

```default_code= 'parse_error'```

```default_detail```

```status_code= 400```
___

```
exceptionzibanu.django.rest_framework.exceptions.PermissionDenied(detail=None, code=None)
```

```default_code= 'permission_denied'```

```default_detail```

```status_code= 403```
___

```
exceptionzibanu.django.rest_framework.exceptions.UnsupportedMediaType(media_type, detail=None, code=None)
```

```default_code= 'unsupported_media_type'```

```default_detail```

```status_code= 415```

___

```
exceptionzibanu.django.rest_framework.exceptions.ValidationError(detail=None, code=None)
```

```default_code= 'invalid'```

```default_detail```

```status_code= 400```

## zibanu.django.rest_framework.fields package

Este paquete contiene campos personalizados para Django REST Framework.

### zibanu.django.rest_framework.fields.current_user_default module

Este modulo proporciona una clase personalizada `CurrentUserDefault` que es compatible con el objeto de usuario SimpleJWT.

### zibanu.django.rest_framework.fields.hybrid_image module
```
classzibanu.django.rest_framework.fields.hybrid_image.HybridImageField(*args, **kwargs)
```

Clase heredada de drf_extra_fields.field.HybridImageField para permitir la validación del tamaño e implementar la imagen de uso validación de formato y tamaño.


**Métodos**

```
to_internal_value(data)→ 
```

Método de anulación para procesar datos internos del serializador.

Parámetros:

- ```data:``` Datos recibidos del serializador (datos de publicación sin procesar).

Retorna:

- Compatible con datos de Python.
_____

## zibanu.django.rest_framework.serializers package

Este paquete proporciona un conjunto de serializadores personalizados para usar con Django REST Framework.


### zibanu.django.rest_framework.serializers.model_serializer module

```
classzibanu.django.rest_framework.serializers.model_serializer.ModelSerializer(*args, **kwargs)
```


Este módulo proporciona una clase ModelSerializer personalizada que anula el ModelSerializer predeterminado proporcionado por Django REST Framework.



### zibanu.django.rest_framework.serializers.fields module

Este módulo contiene el siguiente campo de serializador:

* `CurrentUserDefault`: Un campo que establece el campo `user` como el usuario actual.

## zibanu.django.rest_framework.viewsets package

Este paquete contiene un conjunto de conjuntos de vistas personalizados que se pueden usar con Django REST Framework.

### zibanu.django.rest_framework.viewsets.model_viewset module

Este repositorio contiene una versión modificada de la clase ModelViewSet de Django REST Framework

```
classzibanu.django.rest_framework.viewsets.model_viewset.ModelViewSet(*args, **kwargs)
```

Clase heredada de rest_framework.viewsets.ModelViewSet para anular.


**Métodos**

```
get_queryset(**kwargs)→ QuerySet:
```

Obtenga un conjunto de consultas del modelo a partir de los parámetros **kwargs. Si desea queryset pk se base en, envíe la clave "pk" en kwargs.

Parámetros:

- ```**kwargs:``` Diccionario con parámetros clave y de valor.

Retorna:

- ```qs:``` Objeto de conjunto de consultas del modelo.



___

```
list(request, *args, **kwargs)→ Response:
```

Servicio REST para obtener una lista de registros del modelo definido por clase.

Parámetros:

- ```request:``` Solicitar objeto desde HTTP.

- ```*args:``` Tupla de parámetros.


- ```**kwargs:``` Diccionario de parámetros clave y de valor.


Retorna:

- ```response:``` Objeto de respuesta con estado y lista de conjuntos de datos.

    Estado -> 200 si existen datos

    Estado -> 204 si los datos están vacíos.

___

```
retrieve(request, *args, **kwargs)→ Response:
```

Servicio REST para obtener un registro filtrado por pk.

Parámetros:

- ```request:``` Solicitar objeto desde HTTP.

- ```*args:``` Tupla de parámetros.


- ```**kwargs:``` Diccionario de parámetros clave y de valor.


Retorna:

- ```response:``` Objeto de respuesta con estado.

    Estado -> 200 si existe registro y registro de datos.

    Si el registro no existe, se lanza una excepción.


___

```
create(request, *args, **kwargs)→ Response:
```

Servicio REST para crear un registro de modelo.

Parámetros:

- ```request:``` Solicitar objeto desde HTTP.

- ```*args:``` Tupla de parámetros.


- ```**kwargs:``` Diccionario de parámetros clave y de valor.


Retorna:

- ```response:``` Objeto de respuesta con estado.

    Estado -> 201 si se realizó correctamente y registro creado a partir del objeto modelo.


____



```
update(request, *args, **kwargs)→ Response:
```

Servicio REST para actualizar un registro existente del modelo.

Parámetros:

- ```request:``` Solicitar objeto desde HTTP.

- ```*args:``` Tupla de parámetros.


- ```**kwargs:``` Diccionario de parámetros clave y de valor.


Retorna:

- ```response:``` Objeto de respuesta con estado.

    Estado -> 200 si se realiza correctamente y registro actualizado desde el objeto modelo.

____



```
destroy(request, *args, **kwargs)→ Response:
```

Servicio REST para eliminar un registro del modelo.

Parámetros:

- ```request:``` Solicitar objeto desde HTTP.

- ```*args:``` Tupla de parámetros.


- ```**kwargs:``` Diccionario de parámetros clave y de valor.


Retorna:

- ```response:``` Objeto de respuesta con estado.

    Estado -> 200 si se realiza correctamente.

____

### zibanu.django.rest_framework.viewsets.viewset module

```
classzibanu.django.rest_framework.viewsets.viewset.ViewSet(RestViewSet)
```

Esta es una clase ViewSet personalizada que hereda de la clase `rest_framework.viewsets.ViewSet`.

Define las permission_classes  y authentication_classes  predeterminadas para todos los conjuntos de vistas que heredan de él.



______________________






## Paquete de Plantillas de Zibanu para Django (zibanu.django.template package)

Este repositorio contiene procesadores de contexto para Django.

### zibanu.django.template.apps module

```
classzibanu.django.template.apps.ZbDjangoTemplate(app_name, app_module)
```

Clase heredada de django.apps.AppConfig para definir la configuración de zibanu.django.template

```default_auto_field= 'django.db.models.BigAutoField'```

```name= 'zibanu.django.template'```

## zibanu.django.template.context_processors package

Este paquete contiene procesadores de contexto para Django.


### zibanu.django.template.context_processors.full_static_uri module

```
zibanu.django.template.context_processors.full_static_uri.full_static_uri(request)
```

Preprocesador de contexto para obtener "full_static_uri", incluido el nombre de host y el uri estático para el uso de la plantilla.

Parámetros:

- ```request:``` Solicitar objeto desde HTTP.

Retorna:

- ```full_uri:``` Diccionario con clave/valor "full_static_uri".

## zibanu.django.template.context_processors.site module

```
zibanu.django.template.context_processors.site.site(request)
```
Preprocesador de contexto para obtener la uri absoluta del sitio para usar en plantillas de Django.

Parámetros:

- ```request:``` Solicitar objeto desde HTTP.

Retorna:

- ```site_uri:``` Diccionario con clave/valor del sitio.

## zibanu.django.template.templatetags package

Este repositorio contiene etiquetas de plantilla personalizadas para Django.


### zibanu.django.template.templatetags.static_uri module

```
classzibanu.django.template.templatetags.static_uri.StaticNodeUri(uri_string: str)
```

Clase heredada de django.template.Node para permitir el uso de la etiqueta de plantilla "static_uri" en las plantillas de Django.

___

**Métodos** 

```
zibanu.django.template.templatetags.static_uri.render(context)
```
Anular el método para representar la etiqueta en la plantilla.

Parámetros:

- ```context:``` Objeto de diccionario de contexto de plantilla.

Retorna:

- ```uri:``` Cadena para renderizar en plantilla.


**Función**

```
zibanu.django.template.templatetags.static_uri.static_uri(parse, token)
```

Función para registrar etiqueta en plantilla.

Parámetros:

- ```parse:``` Analizar objeto de plantilla.
- ```token:``` Objeto token de plantilla.

Retorna:

- La clase StaticNodeUri se llamará desde la plantilla y se representará.



### zibanu.django.template.templatetags.string_concat module

```
zibanu.django.template.templatetags.string_concat.string_concat(first_string: str, *args)
```

Etiqueta simple para concatenar una cadena con tupla de cadenas.

Parámetros:

- ```first_string:``` Cadena base para concatenar.

- ```args:``` Tupla de cadenas.


Retorna:

- Cadena concatenada.

### zibanu.django.template.templatetags.subtotal_dict module

```
zibanu.django.template.templatetags.subtotal_dict.subtotal_dict(source_list: list, key_control: str, *args)→ list
```

Etiqueta de plantilla para obtener un subtotal de una lista de registros del diccionario.

Parámetros:

- ```source_list:``` Lista con todos los datos del diccionario.

- ```key_control:``` Uso de claves para indexar y realizar los desgloses de subtotales.

- ```args:``` Tupla con lista de nombres clave para obtener los subtotales.

Retorna:

- ```return_list:``` Lista con un diccionario de datos con las claves "control", "totales" y datos", que contiene los subtotales como este:

Control -> Valor de source_list para la clave key_control.

Totals -> Total para key_control.

Data -> Lista con datos de source_list con una clave diferente del valor del parámetro key_control.


### zibanu.django.template.templatetags.sum_dict module

```
zibanu.django.template.templatetags.sum_dict.sum_dict(source_list: list, key: str, format_string: str | None = None)
```

Etiqueta de plantilla para obtener una suma de una lista de registros del diccionario.

Parámetros:

- ```source_list:``` Lista con registros de dictado.

- ```key:``` Nombre de la cadena clave para realizar la suma.

- ```format_string:``` Formato que se utilizará en la plantilla de renderizado.

Retorna:

- ```f_sum:``` Cadena con resultado formateado de la operación de suma.




________________




## Paquete de Utilidades de Zibanu para Django (zibanu.django.utils package)

Este paquete contiene clases de utilidad y funciones para Zibanu Django.

Estas son algunas de las clases de utilidades y funciones en este paquete:

* [CodeGenerator](#zibanudjangoutilscode_generator-module):
 Esta clase se utiliza para generar diferentes tipos de códigos de forma aleatoria.
* [ErrorMessages](#zibanudjangoutilserror_messages-module): Esta clase contiene constantes de compilación de mensajes de error.
* [Mail](#zibanudjangoutilsmail-module): Esta clase se hereda de la clase EmailMultiAlternatives para crear un correo electrónico a partir de una plantilla html y texto html.
* [Datetime](#zibanudjangoutilsdate_time-module): Esta clase contiene funciones para cambiar la zona horaria y agregar la zona horaria a un valor de fecha y hora.
* [Request_Utils](#zibanudjangoutilsrequest_utils-module): Obtiene la dirección IP de la solicitud.
* [User](#zibanudjangoutilsuser-module): Función para obtener usuario del token SimpleJWT TokenUser o usuario de Django.


## APIs

### Lista de zonas horarias (Timezone List)
Servicio REST para listar las zonas horarias disponibles.

Parámetros:

- Request: Solicitar objeto de HTTP.

Retorna:

- Objeto Response con estado HTTP 200 y lista de zonas horarias.
____


## zibanu.django.utils.code_generator module

```
class zibanu.django.utils.code_generator.CodeGenerator(action: str, is_safe: bool = True, code_length: int = 6)
```

Clase para generar diferentes tipos de código de forma aleatoria. Esta clase tiene la capacidad de generar códigos numéricos, códigos alfanuméricos y códigos seguros, según sea necesario, además, puede generar un identificador único universal (UUID).

Parámetros:

- ```'action: str':``` Código de acción para referenciarlo en la caché si es necesario.

- ```'is_safe: bool':``` Bandera para indicar si se utiliza el modo seguro de UUID.

- ```'code_lenght: int':``` La longitud del código que se va a generar (por defecto es 6).


Propiedades:

- ```'action():``` Obtiene el valor de __action.

Retorna:
Valor de tipo cadena con la descripción de la acción.


- ```'is_safe():``` Obtiene el valor de _uuid_safe.

Retorna:
Parámetro booleano, verdadero si el UUID usa el modo seguro; de lo contrario, falso.

- ```'code()':``` Obtiene el valor de __code.

Retorna:
Valor de tipo de cadena con el código generado.

____
**Métodos**


```
get_numeric_code(length: int | None = None)→ str
```

Obtener un código numérico con la longitud definida en el constructor o recibida como parámetro "length" en este método.

Parámetros:

- ```length:``` Longitud del código generado. Anular la longitud definida en la clase.

Retorna:

- Una cadena con el código numérico.

____

```
get_alpha_numeric_code(length: int | None = None)→ str
```

Obtener un código alfanumérico con la longitud definida en el constructor o recibida como parámetro "length" en este método.

Parámetros:

- ```length:``` Longitud del código generado. Este parámetro anula la longitud definida en la clase.


Retorna:

- Una cadena con el código numérico.

____

```
get_secure_code(length: int | None = None)→ str
```
Obtener un código seguro con la longitud definida en el constructor o recibida como parámetro "length" en este método.

Parámetros:

- ```length:``` Longitud del código generado. Este parámetro anula la longitud definida en la clase.

Retorna:

- Una cadena con el código numérico.

____
```
generate_uuid()→ bool
```
Método para generar un UUID en modo seguro, dependiendo del parámetro establecido en el constructor.

Retorna:

- True si se genera con éxito, de lo contrario, False.
____

```
generate_dict(is_numeric: bool = True)→ dict
```

Método para generar un diccionario con uuid, code y action.

Parámetros: 

- ```is_numeric:``` Bandera para indicar si el código generado es numérico o alfanumérico.

Retorna:

- Diccionario con las claves uuid, code y action.


____

## zibanu.django.utils.error_messages module

```
class zibanu.django.utils.error_messages.ErrorMessages
```

Clase que contiene constantes o mensajes de error utilizados a través de la API de Django. Estos mensajes de error se pueden utilizar para proporcionar información detallada sobre el tipo de error que se ha producido y así facilitar la depuración y el manejo adecuado de excepciones en el código.

Constantes

- *FIELD_REQUIRED:* El campo es obligatorio

- *CREATE_ERROR:* No se ha creado el registro.

- *UPDATE_ERROR:* El registro no ha sido actualizado.

- *NOT_FOUND:* No hay coincidencia de registros.

- *DELETE_ERROR:* El registro no se puede eliminar.

- *DATA_REQUIRED:* Los datos requeridos no se encuentran.

- *DATABASE_ERROR:* Error en la base de datos.

- *DATA_REQUEST_NOT_FOUND:* Datos requeridos en la solicitud no encontrados.

- *NOT_CONTROLLED:* Excepción no controlada.

____

## zibanu.django.utils.mail module

```
class zibanu.django.utils.mail.Email(subject: str = '', body: str = '', from_email: str | None = None, to: list | None = None, bcc: list | None = None, connection: Any | None = None, attachments: list | None = None, headers: dict | None = None, cc: list | None = None, reply_to: list | None = None, context: dict | None = None)
```

Clase para realizar envíos de correos electrónicos a partir de un template html o texto o de lo contrario, por medio de un asunto.

Parámetros:


- ```'subject: str':``` Asunto del correo electrónico.

- ```'body: str':``` Texto del cuerpo del correo electrónico.

- ```'from_email: str':``` De la dirección de correo electrónico

- ```'to: list':``` Lista o tupla de direcciones de destinatarios.

- ```'bcc: list':``` Una lista o tupla de direcciones utilizadas en el encabezado "Bcc" al enviar el correo electrónico.

- ```'connection: Any':``` Instancia de conexión de back-end de correo electrónico.

- ```'attachments: list':``` Lista de archivos adjuntos.

- ```'headers: dict':``` Un diccionario de encabezados adicionales para poner en el mensaje. Las claves son el nombre del encabezado, los valores son los valores del encabezado.

- ```'cc: list':``` Una lista o tupla de la dirección del destinatario utilizada en el encabezado "Cc" al enviar el correo electrónico.

- ```'reply_to: list':``` Una lista o tupla de direcciones de destinatarios utilizadas en el encabezado "Responder a" al enviar el correo electrónico.

- ```'context: dict':``` Diccionario de contexto para algunas variables adicionales.
____
**Métodos**

```
send(fail_silently=False)
```
Anule el método para enviar un mensaje de correo electrónico.


Parámetros:

- ```fail_silently:``` Indicador para determinar si se detecta un error o no.

____
```
set_html_template(template: str, context: dict | None = None)
```
Establezca una plantilla html para la construcción del correo electrónico del cuerpo.

Parámetros:

- ```template:``` Ruta completa y nombre de archivo de la plantilla.


- ```context:``` Diccionario de contexto con vars adicionales.

____
```
set_text_template(template: str, context: dict | None = None)
```
Establezca una plantilla de texto para el cuerpo del correo electrónico.

Parámetros:

- ```template:``` Ruta completa y nombre de archivo de la plantilla.

- ```context:``` Diccionario de contexto con vars adicionales.


## zibanu.django.utils.date_time module

```
zibanu.django.utils.date_time.change_timezone(date_to_change: datetime, tz: ZoneInfo | None = None)→ datetime
```

Función para cambiar la zona horaria a un valor de fecha y hora.

Parámetros:

- ```date_to_change:``` Valor de fecha y hora para cambiar la zona horaria

- ```tz:``` Zona horaria a la que se le asignará un valor de fecha y hora


Retorna:

- Fecha y hora con una nueva zona horaria.

____

```
zibanu.django.utils.date_time.add_timezone(date_to_change: datetime, tz: ZoneInfo | None = None)→ datetime
```

Función para agregar la zona horaria a un valor de fecha y hora ingenuo.

Parámetros:

- ```date_to_change:``` Valor de fecha y hora ingenuo para agregar zona horaria.


- ```tz:``` Zona horaria a la que se le asignará un valor de fecha y hora.

Retorna:

- Fecha y hora con una nueva zona horaria.





### zibanu.django.utils.request_utils module

```
zibanu.django.utils.request_utils.get_ip_address(request: Any)→ str
```

Obtener dirección IP de la solicitud.







### zibanu.django.utils.user module

```
zibanu.django.utils.user.get_user(user: Any)→ Any
```
Función para obtener usuario del token SimpleJWT TokenUser o usuario de Django.


Parámetros:

- ```user:``` Objeto de usuario para revisión.


Retorna:

- ```local_user:``` Objeto de usuario de Django.

____

```
zibanu.django.utils.user.get_user_object(user: Any)→ Any
```

Función heredada. Utilice "get_user" en su lugar. Esta función se eliminará en versiones futuras.

- ```user:``` Objeto de usuario para revisión.


Retorna:

- ```local_user:``` Objeto de usuario de Django.