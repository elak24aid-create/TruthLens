import 'package:flutter_test/flutter_test.dart';
import 'package:truthlens_app/features/shell/main_navigation_scaffold.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('TruthLens App renders and navigation operates correctly',
      (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: MainNavigationScaffold(),
    ));
    await tester.pump();

    // Verify app bar title
    expect(find.text('TruthLens'), findsWidgets);

    // Verify navigation destinations
    expect(find.text('Home'), findsOneWidget);
    expect(find.text('Check News'), findsOneWidget);
    expect(find.text('History'), findsOneWidget);
    expect(find.text('Profile'), findsOneWidget);

    // Tap Check News tab
    await tester.tap(find.text('Check News'));
    await tester.pump(const Duration(seconds: 1));

    // Verify Check News tab content
    expect(find.text('Text / Headline'), findsOneWidget);
    expect(find.text('Article URL'), findsOneWidget);
    expect(find.text('Analyze News'), findsOneWidget);
  });
}
