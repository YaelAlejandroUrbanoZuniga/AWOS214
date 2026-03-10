import { useEffect, useState, useCallback } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    FlatList,
    StyleSheet,
    Alert,
    ActivityIndicator
} from 'react-native';

const API_URL = "http://10.16.34.249:5000/v1/usuarios";

class UsuarioController {

    listeners = [];

    addListener(callback) {
        this.listeners.push(callback);
    }

    removeListener(callback) {
        this.listeners = this.listeners.filter(l => l !== callback);
    }

    notify() {
        this.listeners.forEach(l => l());
    }

    async obtenerUsuarios() {
        const response = await fetch(API_URL);
        return await response.json();
    }

    async crearUsuario(id, nombre, edad) {

        const nuevoUsuario = {
            id: parseInt(id),
            nombre: nombre,
            edad: parseInt(edad)
        };

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(nuevoUsuario)
        });

        this.notify();
        return await response.json();
    }

    async actualizarUsuario(id, nombre, edad) {

        const usuario = {
            id: parseInt(id),
            nombre: nombre,
            edad: parseInt(edad)
        };

        const response = await fetch(`${API_URL}/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(usuario)
        });

        this.notify();
        return await response.json();
    }

    async eliminarUsuario(id) {

        await fetch(`${API_URL}/${id}`, {
            method: "DELETE"
        });

        this.notify();
    }

}

const controller = new UsuarioController();

export default function UsuarioView() {

    const [usuarios, setUsuarios] = useState([]);
    const [id, setId] = useState('');
    const [nombre, setNombre] = useState('');
    const [edad, setEdad] = useState('');
    const [editing, setEditing] = useState(false);
    const [loading, setLoading] = useState(true);

    const cargarUsuarios = useCallback(async () => {

        setLoading(true);
        const data = await controller.obtenerUsuarios();
        setUsuarios(data);
        setLoading(false);

    }, []);

    useEffect(() => {

        cargarUsuarios();

        controller.addListener(cargarUsuarios);

        return () => {
            controller.removeListener(cargarUsuarios);
        };

    }, [cargarUsuarios]);


    const guardarUsuario = async () => {

        if (!id || !nombre || !edad) {
            Alert.alert("Error", "Completa todos los campos");
            return;
        }

        if (editing) {

            await controller.actualizarUsuario(id, nombre, edad);
            Alert.alert("Actualizado", "Usuario actualizado");

        } else {

            await controller.crearUsuario(id, nombre, edad);
            Alert.alert("Creado", "Usuario agregado");

        }

        setId('');
        setNombre('');
        setEdad('');
        setEditing(false);

    };


    const editarUsuario = (usuario) => {

        setId(usuario.id.toString());
        setNombre(usuario.nombre);
        setEdad(usuario.edad.toString());
        setEditing(true);

    };


    const eliminarUsuario = (id) => {

        Alert.alert(
            "Eliminar",
            "¿Seguro que deseas eliminar este usuario?",
            [
                { text: "Cancelar" },
                {
                    text: "Eliminar",
                    onPress: async () => {
                        await controller.eliminarUsuario(id);
                        Alert.alert("Eliminado", "Usuario eliminado");
                    }
                }
            ]
        );

    };


    const renderUsuario = ({ item }) => (

        <View style={styles.card}>

            <View style={{ flex: 1 }}>
                <Text style={styles.nombre}>{item.nombre}</Text>
                <Text style={styles.info}>ID: {item.id}</Text>
                <Text style={styles.info}>Edad: {item.edad}</Text>
            </View>

            <View style={styles.buttonsRow}>

                <TouchableOpacity
                    style={styles.editButton}
                    onPress={() => editarUsuario(item)}
                >
                    <Text style={styles.buttonText}>Editar</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.deleteButton}
                    onPress={() => eliminarUsuario(item.id)}
                >
                    <Text style={styles.buttonText}>Eliminar</Text>
                </TouchableOpacity>

            </View>

        </View>

    );

    return (

        <View style={styles.container}>

            <Text style={styles.title}>CRUD USUARIOS</Text>

            <View style={styles.form}>

                <TextInput
                    style={styles.input}
                    placeholder="ID"
                    value={id}
                    onChangeText={setId}
                />

                <TextInput
                    style={styles.input}
                    placeholder="Nombre"
                    value={nombre}
                    onChangeText={setNombre}
                />

                <TextInput
                    style={styles.input}
                    placeholder="Edad"
                    value={edad}
                    onChangeText={setEdad}
                />

                <TouchableOpacity
                    style={styles.mainButton}
                    onPress={guardarUsuario}
                >
                    <Text style={styles.buttonText}>
                        {editing ? "Actualizar Usuario" : "Agregar Usuario"}
                    </Text>
                </TouchableOpacity>

            </View>

            {loading ? (
                <ActivityIndicator size="large" color="#2ecc71" />
            ) : (

                <FlatList
                    data={usuarios}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={renderUsuario}
                />

            )}

        </View>

    );

}


const styles = StyleSheet.create({

    container: {
        flex: 1,
        backgroundColor: "#f2f2f2",
        paddingTop: 60,
        paddingHorizontal: 20
    },

    title: {
        fontSize: 28,
        fontWeight: "bold",
        textAlign: "center",
        marginBottom: 20,
        color: "#2ecc71"
    },

    form: {
        backgroundColor: "#fff",
        padding: 20,
        borderRadius: 12,
        marginBottom: 20
    },

    input: {
        borderWidth: 1,
        borderColor: "#ddd",
        padding: 12,
        borderRadius: 8,
        marginBottom: 10
    },

    mainButton: {
        backgroundColor: "#27ae60",
        padding: 15,
        borderRadius: 10,
        alignItems: "center"
    },

    buttonText: {
        color: "#fff",
        fontWeight: "bold"
    },

    card: {
        flexDirection: "row",
        backgroundColor: "#fff",
        padding: 15,
        borderRadius: 10,
        marginBottom: 10,
        alignItems: "center"
    },

    nombre: {
        fontSize: 16,
        fontWeight: "bold"
    },

    info: {
        fontSize: 13,
        color: "#666"
    },

    buttonsRow: {
        flexDirection: "row",
        gap: 10
    },

    editButton: {
        backgroundColor: "#2ecc71",
        padding: 10,
        borderRadius: 8
    },

    deleteButton: {
        backgroundColor: "#e74c3c",
        padding: 10,
        borderRadius: 8
    }

});