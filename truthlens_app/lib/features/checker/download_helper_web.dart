// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

void downloadTextFile(String text, String filename) {
  final bytes = text.codeUnits;
  final blob = html.Blob([bytes]);
  final url = html.Url.createObjectUrlFromBlob(blob);
  final anchor = html.DocumentFragment.html('<a href="$url" download="$filename"></a>').querySelector('a') as html.AnchorElement;
  
  anchor.click();
  html.Url.revokeObjectUrl(url);
}
