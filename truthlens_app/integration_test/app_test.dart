import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:truthlens_app/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('E2E Test: Full App Verification', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    // STEP 2: TEST LOGIN / SIGN UP
    // Verify Splash / Login screen appears
    expect(find.text('TruthLens'), findsWidgets);
    
    // Tap "Sign Up" if it exists
    final signUpButton = find.text('Sign Up');
    if (signUpButton.evaluate().isNotEmpty) {
      await tester.tap(signUpButton);
      await tester.pumpAndSettle();
      
      // Should be on Sign Up screen
      expect(find.text('Create Account'), findsWidgets);
      
      // Go back to login
      final backToLogin = find.text('Already have an account? Login');
      if (backToLogin.evaluate().isNotEmpty) {
        await tester.tap(backToLogin);
        await tester.pumpAndSettle();
      }
    }

    // Enter login credentials (mock/test credentials)
    final emailField = find.byType(TextField).first;
    await tester.enterText(emailField, 'test@example.com');
    
    final passwordField = find.byType(TextField).last;
    await tester.enterText(passwordField, 'password123');
    
    final loginButton = find.text('Login');
    await tester.tap(loginButton);
    await tester.pumpAndSettle(const Duration(seconds: 2));

    // STEP 3: TEST HOME
    expect(find.text('Daily News'), findsWidgets);
    expect(find.text('Check News'), findsWidgets);

    // STEP 4: TEST DAILY NEWS
    await tester.tap(find.text('Daily News'));
    await tester.pumpAndSettle(const Duration(seconds: 5)); // Wait for RSS fetch
    // Verify News loads
    expect(find.byType(ListTile), findsWidgets);
    
    // STEP 5: TEST TEXT FACT CHECKING
    await tester.tap(find.text('Check News'));
    await tester.pumpAndSettle();

    final textField = find.byType(TextField);
    expect(textField, findsOneWidget);
    
    // Test NASA Claim
    await tester.enterText(textField, 'NASA launches new rover to Mars to study geological formations.');
    await tester.pumpAndSettle();

    final analyzeButton = find.text('Analyze News');
    await tester.tap(analyzeButton);

    // Wait for backend response
    await tester.pumpAndSettle(const Duration(seconds: 10));

    // Verify Result Screen
    expect(find.textContaining('Verdict'), findsWidgets);
    expect(find.textContaining('Confidence'), findsWidgets);
    expect(find.textContaining('Likely Genuine'), findsWidgets);

    // Go back
    final backButton = find.byTooltip('Back');
    await tester.tap(backButton);
    await tester.pumpAndSettle();

    // Test Cancer Claim
    await tester.enterText(textField, 'BREAKING: Shocking miracle cure for cancer discovered by secret government lab! Share before deleted!');
    await tester.pumpAndSettle();
    await tester.tap(analyzeButton);
    await tester.pumpAndSettle(const Duration(seconds: 10));

    expect(find.textContaining('Likely Misleading'), findsWidgets);

    // Go back
    await tester.tap(backButton);
    await tester.pumpAndSettle();

    // STEP 9: TEST HISTORY
    await tester.tap(find.text('History'));
    await tester.pumpAndSettle();
    
    // History should have both checks
    expect(find.textContaining('NASA launches new'), findsWidgets);
    expect(find.textContaining('BREAKING: Shocking miracle'), findsWidgets);

    // STEP 10: TEST COMMUNITY REPORTS
    await tester.tap(find.text('Reports'));
    await tester.pumpAndSettle();
    // Verify it doesn't crash
    expect(find.text('Community Reports'), findsWidgets);

    // STEP 11: TEST PROFILE & LOGOUT
    await tester.tap(find.text('Profile'));
    await tester.pumpAndSettle();
    
    expect(find.text('test@example.com'), findsWidgets);
    
    final logoutButton = find.text('Logout');
    await tester.tap(logoutButton);
    await tester.pumpAndSettle();

    // Verify we are back to Login
    expect(find.text('Login'), findsWidgets);
  });
}
