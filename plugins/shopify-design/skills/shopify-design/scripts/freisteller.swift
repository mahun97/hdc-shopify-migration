import Foundation
import Vision
import CoreImage
import AppKit

// Stellt das Hauptmotiv frei — nutzt den Freisteller des Vision-Frameworks (ab macOS 14).
let args = CommandLine.arguments
guard args.count >= 3 else { print("Aufruf: frei <quelle> <ziel.png>"); exit(1) }
guard let quelle = CIImage(contentsOf: URL(fileURLWithPath: args[1])) else {
    print("FEHLER: Bild nicht lesbar"); exit(1)
}
let anfrage = VNGenerateForegroundInstanceMaskRequest()
let leser = VNImageRequestHandler(ciImage: quelle)
do {
    try leser.perform([anfrage])
    guard let ergebnis = anfrage.results?.first else { print("FEHLER: kein Motiv erkannt"); exit(2) }
    let maskiert = try ergebnis.generateMaskedImage(ofInstances: ergebnis.allInstances,
                                                    from: leser, croppedToInstancesExtent: true)
    let ci = CIImage(cvPixelBuffer: maskiert)
    let ctx = CIContext()
    guard let farbraum = CGColorSpace(name: CGColorSpace.sRGB) else { exit(3) }
    try ctx.writePNGRepresentation(of: ci, to: URL(fileURLWithPath: args[2]),
                                   format: .RGBA8, colorSpace: farbraum)
    print("OK \(Int(ci.extent.width))x\(Int(ci.extent.height))")
} catch { print("FEHLER: \(error)"); exit(4) }
