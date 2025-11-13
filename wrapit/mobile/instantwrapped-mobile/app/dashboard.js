import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, Image, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
// import globalStyles from '../styles/globalStyles';

export default function Dashboard() {
    const [tracks, setTracks] = useState([]);
    const backendUrl = 'http://27.0.0.1:8000';

    useEffect(() => {
        const loadTracks = async () => {
            const token = await AsyncStorage.getItem("spotify_token");
            if (!token) return;
        
        fetch(`${backendUrl}/api/top-tracks/?access_token=${token}`)
            .then(res => res.json())
            .then(data => setTracks(data.top_tracks))
            .catch(err => console.error(err));
        };

        loadTracks();
    }, []);

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Your Top Tracks</Text>
            <FlatList
                data={tracks}
                keyExtractor={(item) => item.name}
                renderItem={({ item }) => (
                    <View style={styles.trackCard}>
                        <Image source={{ uri: item.image}} style={styles.albumArt} />
                        <View style={styles.trackInfo}>
                            <Text style={styles.trackName}>{item.name}</Text>
                            <Text style={styles.artistName}>{item.artist}</Text>
                        </View>
                    </View>
                )}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    constainer: { flex: 1, backgroundColor: '#121212', padding: 20 },
    title: { color: 'White', fontSize: 22, marginBottom: 15 },
    trackCard: { 
        flexDirection: 'row',
        marginBottom: 15,
        alignItems: 'center',
        backgroundColor: '#1E1E1E',
        borderRadius: 10,
        padding: 10,
    },
    albumArt: { width: 60, height: 60, borderRadius: 8, marginRight: 10 },
    trackInfo: { flex: 1 },
    trackName: { color: 'White', fontSize: 16, fontWeight: 'bold' },
    artistName: { color: '#B3B3B3', fontSize: 14 },
});