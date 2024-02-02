# Unreal toolbox

A series of tools developed while learning unreal and airsim scripting.

May serve for reference or as quick-deploy tools.

## Contents

### Airsim

A bunch of scripts for different tasks built with the AirSim python API.

### Blueprints

A collection of varied utilities and assets for world architecture. Includes these topics or more:
- Procedural foliage: few basic assets only 
- Virtual texturing: blueprints for blending the textures of meshes with those of the floor
- Landscape Materials: parameterized grass+dirt landscape material with some customization toys
- Mesh grid: blueprint to lay out grids of meshes
- Road signs: blueprint to create sign posts from PNG transparent images, plus some example assets.


## Useful links

- Airsim docs: https://microsoft.github.io/AirSim/api_docs/html/
- Landscape tutorial playlist: https://www.youtube.com/watch?v=yCRzOdo4b68&list=PLKPWwh_viQMFkprfsJ1pQ7uhn0uPIX8HP
- Virtual textures tutorial: https://www.youtube.com/watch?v=xYuIDFzKaF4
- Mesh grid tutorial: https://www.youtube.com/watch?v=QJIrksZOkgQ
- Road signs tutorial: https://www.youtube.com/watch?v=b8WCXj4PwX0


## Notes dump


gst-launch-1.0 rtspsrc location=rtsp://0.0.0.0:8554/cam0 ! decodebin! queue ! videoconvert ! xvimagesink sync=0 async=0
