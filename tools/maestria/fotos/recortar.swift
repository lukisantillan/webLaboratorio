// Recorta el sujeto de cada foto (Vision, como "Copiar sujeto") y detecta la cara.
// Uso: swift recortar.swift <carpeta_salida> <fotos...>  -> <nombre>.png con transparencia + caras.json
import Foundation
import Vision
import CoreImage

let args = CommandLine.arguments
let salida = URL(fileURLWithPath: args[1])
let ctx = CIContext()
var res: [[String: Any]] = []
for ruta in args.dropFirst(2) {
    let url = URL(fileURLWithPath: ruta)
    guard let img = CIImage(contentsOf: url, options: [.applyOrientationProperty: true]) else { print("no se pudo leer", ruta); continue }
    let handler = VNImageRequestHandler(ciImage: img, options: [:])
    let mascara = VNGenerateForegroundInstanceMaskRequest()
    let caras = VNDetectFaceRectanglesRequest()
    do { try handler.perform([mascara, caras]) } catch { print("error", ruta, error); continue }
    var e: [String: Any] = ["archivo": url.lastPathComponent, "ancho": img.extent.width, "alto": img.extent.height]
    if let obs = mascara.results?.first {
        let buf = try! obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler)
        let m = CIImage(cvPixelBuffer: buf)
        let vacio = CIImage(color: .clear).cropped(to: img.extent)
        let out = img.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: vacio, kCIInputMaskImageKey: m])
        let destino = salida.appendingPathComponent(url.deletingPathExtension().lastPathComponent + ".png")
        try! ctx.writePNGRepresentation(of: out, to: destino, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
        e["instancias"] = obs.allInstances.count
    } else { e["instancias"] = 0 }
    // caja de la cara más grande, normalizada, con origen abajo a la izquierda
    if let f = caras.results?.max(by: { $0.boundingBox.width < $1.boundingBox.width }) {
        let b = f.boundingBox
        e["cara"] = [b.origin.x, b.origin.y, b.size.width, b.size.height]
    }
    e["caras"] = caras.results?.count ?? 0
    res.append(e)
}
let datos = try! JSONSerialization.data(withJSONObject: res, options: [.prettyPrinted, .sortedKeys])
FileManager.default.createFile(atPath: salida.appendingPathComponent("caras.json").path, contents: datos)
print("procesadas:", res.count)
