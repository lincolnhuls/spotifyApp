import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import * as Linking from 'expo-linking';
import 'react-native-reanimated';
import { useColorScheme } from '@/hooks/use-color-scheme';

// ✅ Define deep link config for Expo Router
export const linking = {
  prefixes: [
    'instantwrappedmobile://',              // your app’s custom scheme
    'https://spotifyapp-7lsn.onrender.com', // your Render backend domain
  ],
  config: {
    screens: {
      index: '',
      dashboard: 'dashboard',
      modal: 'modal',
    },
  },
};

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      {/* ✅ Expo Router automatically uses the linking config above */}
      <Stack>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="dashboard" options={{ title: 'Dashboard' }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal', title: 'Modal' }} />
      </Stack>
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}
