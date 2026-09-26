import 'dart:html' as html;

Future<bool> shareTextWeb(String title, String text) async {
  try {
    await html.window.navigator.share({
      'title': title,
      'text': text,
    });
    return true;
  } catch (e) {
    // Web share not supported or failed
  }
  return false;
}
