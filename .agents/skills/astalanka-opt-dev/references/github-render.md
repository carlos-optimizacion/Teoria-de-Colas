# Gestión de hitos, GitHub y Render

## Antes de implementar

Inspeccionar estado real de main, SHA, issues abiertos, PR, workflow definitions y archivos afectados. Conservar código existente y no cambiar módulos ajenos. Abrir rama por hito con issue asociado y alcance verificable.

## Flujo de validación

Cambios -> pruebas locales -> PR -> CI del HEAD exacto -> revisión de fallos y capturas -> merge si corresponde. No relajar pruebas para forzar aprobación ni afirmar que una suite ejecutó algo que sus triggers no incluyen.

## Despliegue controlado

Publicar solo con autorización vigente para ese alcance y evidencias verdes. Confirmar Render workspace/service correctos, evitar despliegues duplicados cuando hay autodeploy. Verificar deploy LIVE y SHA igual al merge final, salud, arranque y logs recientes. No cerrar issue ni anunciar publicación si la construcción está pendiente, falla o tiene commit diferente.

## Informe breve del hito

Objetivo; código y módulos realmente modificados; enlaces a issue/PR, commit y CI; lista de pruebas aprobadas y no ejecutadas; screenshots si hay 3D; URL/commit Render y estado exacto; riesgos residuales; siguiente hito.

No prometer trabajo en segundo plano sin automatización creada y observable. No almacenar credenciales o datos confidenciales en repositorio.