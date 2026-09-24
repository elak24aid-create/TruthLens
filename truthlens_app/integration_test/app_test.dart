import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:truthlens_app/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('E2E Test: Check News Flow', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    // Verify Startup
    expect(find.text('TruthLens'), findsWidgets);

    // Navigate to Check News
    await tester.tap(find.text('Check News'));
    await tester.pumpAndSettle();

    // Find the text field and enter text
    final textField = find.byType(TextField);
    expect(textField, findsOneWidget);
    
    await tester.enterText(textField, 'NASA confirms that Earth is a planet in the Solar System.');
    await tester.pumpAndSettle();

    // Tap Analyze News button
    final analyzeButton = find.text('Analyze News');
    expect(analyzeButton, findsOneWidget);
    await tester.tap(analyzeButton);

    // Wait for the network request to finish and result screen to appear
    await tester.pumpAndSettle(const Duration(seconds: 10));

    // Verify we are on the result screen and see the verdict
    expect(find.textContaining('Verdict'), findsWidgets);
    expect(find.textContaining('Confidence'), findsWidgets);
    
    // Check if History was saved
    final backButton = find.byTooltip('Back');
    if (backButton.evaluate().isNotEmpty) {
      await tester.tap(backButton);
      await tester.pumpAndSettle();
    }
    
    await tester.tap(find.text('History'));
    await tester.pumpAndSettle();
    
    // Wait a bit to ensure history loads
    expect(find.textContaining('NASA confirms that Earth'), findsWidgets);
  });
}
