import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';

const broker = 'localhost'; // ggf. IP des PCs/Servers
const port = 1883;
const topicTemperature = 'factory/lightcell/telemetry/temperature';
const topicStateCooling = 'factory/lightcell/state/cooling';
const topicCmdSetpoint = 'factory/lightcell/command/setpoint';
const topicCmdMode = 'factory/lightcell/command/mode';

void main() {
  runApp(const SmartFactoryApp());
}

class SmartFactoryApp extends StatelessWidget {
  const SmartFactoryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Factory Light Cell',
      theme: ThemeData.dark(),
      home: const DashboardPage(),
    );
  }
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  late MqttServerClient client;

  double? temperature;
  bool coolingOn = false;
  String mode = 'AUTO';
  double setpoint = 28.0;
  final TextEditingController _setpointController =
      TextEditingController(text: '28.0');

  @override
  void initState() {
    super.initState();
    _connect();
  }

  Future<void> _connect() async {
    client = MqttServerClient(broker, 'flutter-hmi');
    client.port = port;
    client.logging(on: false);
    client.keepAlivePeriod = 20;
    client.onDisconnected = _onDisconnected;

    final connMess = MqttConnectMessage()
        .withClientIdentifier('flutter-hmi')
        .startClean()
        .withWillQos(MqttQos.atMostOnce);
    client.connectionMessage = connMess;

    try {
      await client.connect();
    } catch (e) {
      debugPrint('Connection failed: $e');
      client.disconnect();
      return;
    }

    if (client.connectionStatus?.state == MqttConnectionState.connected) {
      debugPrint('Connected to MQTT broker');
      client.subscribe(topicTemperature, MqttQos.atMostOnce);
      client.subscribe(topicStateCooling, MqttQos.atMostOnce);

      client.updates?.listen((List<MqttReceivedMessage<MqttMessage>> c) {
        final recMess = c[0].payload as MqttPublishMessage;
        final pt =
            MqttPublishPayload.bytesToStringAsString(recMess.payload.message);

        final topic = c[0].topic;
        debugPrint('Received message on $topic: $pt');

        setState(() {
          if (topic == topicTemperature) {
            try {
              final data = jsonDecode(pt);
              temperature = (data['temperature'] as num).toDouble();
            } catch (_) {}
          } else if (topic == topicStateCooling) {
            try {
              final data = jsonDecode(pt);
              temperature = (data['temperature'] as num).toDouble();
              coolingOn = data['cooling_on'] as bool;
              mode = data['mode'] as String;
              setpoint = (data['setpoint'] as num).toDouble();
            } catch (_) {}
          }
        });
      });
    } else {
      debugPrint(
          'Connection failed: ${client.connectionStatus?.state.toString()}');
      client.disconnect();
    }
  }

  void _onDisconnected() {
    debugPrint('Disconnected from MQTT broker');
  }

  void _publishSetpoint() {
    if (client.connectionStatus?.state != MqttConnectionState.connected) return;

    final value = double.tryParse(_setpointController.text);
    if (value == null) return;

    final payload = jsonEncode({'setpoint': value});
    final builder = MqttClientPayloadBuilder();
    builder.addString(payload);

    client.publishMessage(
      topicCmdSetpoint,
      MqttQos.atMostOnce,
      builder.payload!,
    );
  }

  void _publishMode(String newMode) {
    if (client.connectionStatus?.state != MqttConnectionState.connected) return;

    final payload = jsonEncode({'mode': newMode});
    final builder = MqttClientPayloadBuilder();
    builder.addString(payload);

    client.publishMessage(
      topicCmdMode,
      MqttQos.atMostOnce,
      builder.payload!,
    );
  }

  @override
  void dispose() {
    client.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tempText =
        temperature != null ? '${temperature!.toStringAsFixed(2)} °C' : '---';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Factory Light Cell'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text('Temperatur', style: Theme.of(context).textTheme.headlineSmall),
            Text(tempText, style: Theme.of(context).textTheme.displaySmall),
            const SizedBox(height: 24),
            Text('Kühlung: ${coolingOn ? "EIN" : "AUS"}',
                style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            Text('Mode: $mode'),
            Text('Setpoint: ${setpoint.toStringAsFixed(1)} °C'),
            const SizedBox(height: 32),
            Text('Setpoint ändern'),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _setpointController,
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(
                      labelText: 'Setpoint (°C)',
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _publishSetpoint,
                  child: const Text('Senden'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text('Mode wählen'),
            Row(
              children: [
                ElevatedButton(
                  onPressed: () => _publishMode('AUTO'),
                  child: const Text('AUTO'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _publishMode('MANUAL'),
                  child: const Text('MANUAL'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
