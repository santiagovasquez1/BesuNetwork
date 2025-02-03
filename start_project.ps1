# build.ps1

# --- Validación y eliminación de la imagen genesis-generator:latest ---

# $images = @(
#     @{
#         Name         = "genesis-generator:latest"
#         BuildContext = "."
#         Dockerfile   = ""  # Se usará el Dockerfile por defecto
#     },
#     @{
#         Name         = "node-besu:latest"
#         BuildContext = "."
#         Dockerfile   = ".\NodeDockerfile"
#     }
# )

# foreach ($img in $images) {
#     Write-Host "Procesando imagen: $($img.Name)"

#     # Verificar si la imagen existe (se obtiene el ID)
#     $imageId = docker images -q $($img.Name)
#     if ($imageId) {
#         Write-Host "La imagen '$($img.Name)' ya existe. Eliminándola..."
#         docker rmi -f $($img.Name)
#     }
#     else {
#         Write-Host "La imagen '$($img.Name)' no existe. Procediendo con la construcción."
#     }

#     # Construir la imagen según si se especificó un Dockerfile
#     if ($img.Dockerfile -and $img.Dockerfile.Trim() -ne "") {
#         Write-Host "Construyendo la imagen '$($img.Name)' usando el Dockerfile: $($img.Dockerfile)..."
#         docker build -t $($img.Name) -f $($img.Dockerfile) $($img.BuildContext)
#     }
#     else {
#         Write-Host "Construyendo la imagen '$($img.Name)' usando el Dockerfile por defecto..."
#         docker build -t $($img.Name) $($img.BuildContext)
#     }

#     Write-Host "Cargando la imagen '$($img.Name)' en minikube..."
#     minikube image load $($img.Name)

# }

# Crea el deployment y el servicio para genesis-generator
Write-Host "Aplicando los recursos de Kubernetes..."
kubectl apply -f .\k8s\namespace.yaml
kubectl apply -f .\k8s\configmap-genesis-config-files.yaml
kubectl apply -f .\k8s\genesis-network-pvc.yaml
kubectl apply -f .\k8s\genesis-generator-deployment.yaml
kubectl apply -f .\k8s\debug-pv-deployment.yaml
kubectl apply -f .\k8s\besu-node-service.yaml
kubectl apply -f .\k8s\besu-node-statefulset.yaml