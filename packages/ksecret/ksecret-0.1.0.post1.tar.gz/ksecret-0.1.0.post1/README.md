# 🔑 ksecret: A Kubernetes Secret Helper

`ksecret` is a command-line tool to simplify the management of Kubernetes Secrets. It provides functionalities to encode, decode, and generate Kubernetes Secret YAML files.

## ✨ Features

- **🔐 Encode/Decode Secrets:** Easily encode and decode the `data` field in your Kubernetes Secret files from and to base64.
- **📝 Generate from `.env`:** Create a Kubernetes Secret YAML file directly from a `.env` file.
- **🌱 Generate Environment Variables:** Automatically generate Kubernetes `env` entries for your deployments from Secret and ConfigMap YAML files.

## 🚀 Installation

You can install `ksecret` using pip:

```bash
pip install ksecret
```

## 🛠️ Usage

`ksecret` provides several commands to help you manage your Kubernetes secrets.

### 🔒 Encode a Secret

To base64 encode the values in the `data` field of a Secret YAML file:

```bash
ksecret encode my-secret.yaml
```

This will overwrite the `my-secret.yaml` file with the encoded data. You can specify an output file using the `-o` or `--output` option.

### 🔓 Decode a Secret

To decode the base64 encoded values in the `data` field of a Secret YAML file:

```bash
ksecret decode my-secret.yaml
```

This will overwrite the `my-secret.yaml` file with the decoded data. You can specify an output file using the `-o` or `--output` option.

### 📄 Generate a Secret from a `.env` file

To generate a Kubernetes Secret YAML file from a `.env` file:

```bash
ksecret generate --name my-secret --namespace my-namespace --env-file .env --output my-secret.yaml
```

This will create a new file named `my-secret.yaml` with the generated secret.

### 🌿 Generate Environment Variables from YAMLs

To generate a list of environment variables for a Kubernetes Deployment from Secret and ConfigMap YAML files:

```bash
ksecret generate-env-from-yamls -f my-secret.yaml -f my-configmap.yaml
```

This will print the `env` entries to the console. You can save the output to a file using the `-o` or `--output` option.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on the GitHub repository.

## 📜 License

This project is licensed under the BSD 3-Clause License.
