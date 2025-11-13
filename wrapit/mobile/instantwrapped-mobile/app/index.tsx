import React, { useEffect } from "react";
import { View, Button, StyleSheet, ActivityIndicator, Image } from "react-native";
import * as WebBrowser from "expo-web-browser";
import { makeRedirectUri, useAuthRequest } from "expo-auth-session";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { router } from "expo-router";

WebBrowser.maybeCompleteAuthSession();

export default function HomeScreen() {
  const [loading, setLoading] = React.useState(false);

  // ✅ Your deployed backend
  const backendUrl = "https://spotifyapp-7lsn.onrender.com";

  // ✅ Redirect URI (scheme must match app.json)
  const redirectUri = makeRedirectUri({
    scheme: "instantwrappedmobile", // must match "scheme" in app.json
  });

  console.log("👉 Using redirect URI:", redirectUri);

  // Auth request setup
  const [request, response, promptAsync] = useAuthRequest(
    {
      clientId: "dummy-client-id", // not used — backend handles real Spotify auth
      redirectUri,
      scopes: [],
    },
    { authorizationEndpoint: `${backendUrl}/api/login/` }
  );

  // ✅ Handle redirect after backend sends tokens to Expo
  useEffect(() => {
    const handleResponse = async () => {
      if (response?.type === "success" && response.params.access_token) {
        const { access_token, refresh_token, expires_in } = response.params;
        const expiresInSeconds = Number(expires_in) || 3600;

        console.log("✅ Received Spotify tokens:", {
          access_token,
          refresh_token,
          expires_in,
        });

        await AsyncStorage.setItem("spotify_access_token", access_token);
        await AsyncStorage.setItem("spotify_refresh_token", refresh_token || "");
        await AsyncStorage.setItem(
          "spotify_expires_in",
          String(Date.now() + expiresInSeconds * 1000)
        );

        router.push("/dashboard");
      }
    };
    handleResponse();
  }, [response]);

  const handleLogin = async () => {
    setLoading(true);
    try {
      await promptAsync();
    } catch (err) {
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Image
        source={require("../assets/images/wrapit-banner.png")}
        style={styles.background}
          resizeMode="contain"
      />
      <View style={styles.overlay}>
        {loading ? (
          <ActivityIndicator size="large" color="#1DB954" />
        ) : (
          <View style={styles.buttonContainer}>
            <Button title="Connect with Spotify" color="#1DB954" onPress={handleLogin} />
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  background: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    zIndex: -1,
      backgroundColor: "#000",
  },
  overlay: {
    flex: 1,
    width: "100%",
    justifyContent: "flex-end",
    alignItems: "center",
    paddingBottom: 40,
  },
  buttonContainer: {
    width: "80%",
    marginBottom: 30,
  },
});
