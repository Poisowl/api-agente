"""
ChatBot con flujo interno tipo conversación
El bot maneja internamente todos los flujos y solo responde con mensajes de texto
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, Optional

# =====================================================
# CHATBOT ENGINE
# =====================================================


class ChatBotEngine:
    """Motor del chatbot que maneja flujos internos"""

    def __init__(self, bot_config_path: str = "chatbot.json"):
        bot_config_path = "assets/flow/" + bot_config_path
        with open(bot_config_path, "r", encoding="utf-8") as f:
            self.BOT = json.load(f)["bot"]

        self.SESSIONS = {}

    def get_user_session(self, user_id: str, metadata: Optional[Dict] = None):
        """Inicializa o recupera la sesión de un usuario"""
        if user_id not in self.SESSIONS:
            self.SESSIONS[user_id] = {
                "currentFlow": self.BOT["defaultFlow"],
                "sessionVariables": metadata or {},
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                # Estados para flujos complejos
                "waitingForInput": None,  # tipo de input esperado
                "currentFormField": None,  # campo actual del formulario
                "formFieldIndex": 0,  # índice del campo actual
                "pendingFormData": {},  # datos del formulario en progreso
            }
        else:
            self.SESSIONS[user_id]["last_activity"] = datetime.now().isoformat()
            if metadata:
                self.SESSIONS[user_id]["sessionVariables"].update(metadata)

        return self.SESSIONS[user_id]

    def replace_variables(self, text: str, session_vars: Dict) -> str:
        """Reemplaza {{variable}} por su valor"""
        if not text:
            return ""
        for k, v in session_vars.items():
            text = text.replace(f"{{{{{k}}}}}", str(v))
        return text

    def process_message(
        self,
        user_id: str,
        user_message: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Procesa un mensaje del usuario y retorna solo el texto de respuesta

        Args:
            user_id: ID del usuario
            user_message: Mensaje del usuario (puede ser None en el primer mensaje)
            metadata: Variables iniciales del usuario

        Returns:
            str: Mensaje de texto del bot
        """
        session = self.get_user_session(user_id, metadata)
        session_vars = session["sessionVariables"]

        # Si estamos esperando input de un formulario
        if session["waitingForInput"] == "form":
            return self._handle_form_input(session, user_message)

        # Procesar flujo normal
        return self._process_flow(session, user_message)

    def _process_flow(self, session: Dict, user_input: Optional[str]) -> str:
        """Procesa el flujo actual"""
        current_flow = session["currentFlow"]
        session_vars = session["sessionVariables"]

        flow = self.BOT["flows"].get(current_flow)
        if not flow:
            session["currentFlow"] = self.BOT["errorFlow"]
            return self._process_flow(session, None)

        try:
            flow_type = flow["type"]

            # -------------------- Mensaje simple --------------------
            if flow_type == "message":
                message = self.replace_variables(flow.get("content", ""), session_vars)
                next_flow = flow.get("next", self.BOT["defaultFlow"])
                session["currentFlow"] = next_flow

                # Si el siguiente flujo existe, continuar
                next_flow_obj = self.BOT["flows"].get(next_flow)
                if next_flow_obj:
                    next_message = self._process_flow(session, None)
                    return f"{message}\n\n{next_message}"

                return message

            # -------------------- Opciones / Menú --------------------
            elif flow_type == "options":
                options = flow.get("options", [])

                # Si hay input, procesar la opción seleccionada
                if user_input:
                    user_input_lower = user_input.strip().lower()

                    # Intentar por índice numérico primero
                    if user_input.isdigit():
                        idx = int(user_input) - 1
                        if 0 <= idx < len(options):
                            session["currentFlow"] = options[idx].get(
                                "next", self.BOT["defaultFlow"]
                            )
                            return self._process_flow(session, None)

                    # Buscar por valor o por label
                    for opt in options:
                        if (
                            user_input_lower == opt["value"].lower()
                            or user_input_lower in opt["label"].lower()
                        ):
                            session["currentFlow"] = opt.get(
                                "next", self.BOT["defaultFlow"]
                            )
                            return self._process_flow(session, None)

                    # Opción inválida
                    return f"❌ Opción inválida. {self._format_options(options, flow, session_vars)}"

                # Mostrar opciones
                return self._format_options(options, flow, session_vars)

            # -------------------- Preguntas y Respuestas --------------------
            elif flow_type == "qa":
                questions = flow.get("questions", [])

                if user_input:

                    # Intentar por índice numérico primero
                    if user_input.isdigit():
                        idx = int(user_input) - 1
                        if 0 <= idx < len(questions):
                            q = questions[
                                idx
                            ]  # seleccionamos la pregunta correspondiente
                            session["currentFlow"] = q.get(
                                "next", self.BOT["defaultFlow"]
                            )
                            answer = self.replace_variables(
                                q.get("answer", ""), session_vars
                            )
                            if answer:
                                next_message = self._process_flow(session, None)
                                return f"{answer}\n\n{next_message}"
                            else:
                                return self._process_flow(session, None)

                    # Buscar la pregunta
                    for q in questions:
                        if user_input_lower == q["question"].lower():
                            session["currentFlow"] = q.get(
                                "next", self.BOT["defaultFlow"]
                            )
                            answer = self.replace_variables(
                                q.get("answer", ""), session_vars
                            )
                            if answer:
                                next_message = self._process_flow(session, None)
                                return f"{answer}\n\n{next_message}"
                            else:
                                return self._process_flow(session, None)

                    # Pregunta no encontrada
                    return f"❌ Pregunta no reconocida. {self._format_qa(questions, flow, session_vars)}"

                # Mostrar preguntas
                return self._format_qa(questions, flow, session_vars)

            # -------------------- Formulario --------------------
            elif flow_type == "form":
                fields = flow.get("fields", [])

                # Iniciar el formulario
                if session["currentFormField"] is None:
                    session["waitingForInput"] = "form"
                    session["currentFormField"] = fields[0] if fields else None
                    session["formFieldIndex"] = 0
                    session["pendingFormData"] = {}
                    session["currentFlowData"] = flow  # Guardar el flow completo

                    intro = self.replace_variables(
                        flow.get("content", ""), session_vars
                    )
                    first_field = fields[0]
                    required = " (*)" if first_field.get("required") else ""

                    return f"{intro}\n\n📝 {first_field['label']}{required}"

                # Este caso no debería ocurrir aquí, se maneja en _handle_form_input
                return "Error en el flujo del formulario"

            # -------------------- Conditional --------------------
            elif flow_type == "conditional":
                condition = flow.get("condition")
                condition_str = self.replace_variables(condition, session_vars)

                try:
                    # Evaluar condición de forma segura
                    cond_eval = eval(condition_str, {"__builtins__": {}}, session_vars)
                    next_flow = flow.get("ifTrue") if cond_eval else flow.get("ifFalse")
                    session["currentFlow"] = next_flow
                    return self._process_flow(session, None)
                except:
                    session["currentFlow"] = self.BOT["errorFlow"]
                    return self._process_flow(session, None)

            # -------------------- Dynamic Service --------------------
            elif flow_type == "dynamicService":
                # Simular datos del servicio
                mock_data = [
                    {"id": 1, "nombre": "Servicio A", "precio": "$100"},
                    {"id": 2, "nombre": "Servicio B", "precio": "$200"},
                    {"id": 3, "nombre": "Servicio C", "precio": "$300"},
                ]

                content = self.replace_variables(flow.get("content", ""), session_vars)
                data_text = "\n".join(
                    [f"  • {item['nombre']} - {item['precio']}" for item in mock_data]
                )

                session["currentFlow"] = flow.get("next", self.BOT["defaultFlow"])
                next_message = self._process_flow(session, None)

                return f"{content}\n{data_text}\n\n{next_message}"

        except Exception as e:
            print(f"Error en flujo {current_flow}: {str(e)}")
            session["currentFlow"] = self.BOT["errorFlow"]
            return self._process_flow(session, None)

    def _handle_form_input(self, session: Dict, user_input: str) -> str:
        """Maneja la entrada de datos de un formulario campo por campo"""
        if not user_input:
            return "Por favor, proporciona un valor para este campo."

        current_field = session["currentFormField"]
        flow = session["currentFlowData"]
        fields = flow["fields"]
        session_vars = session["sessionVariables"]

        # Validar el input
        validation = current_field.get("validation")

        if validation:
            # Validar regex
            regex = validation.get("regex")
            if regex and not re.match(regex, user_input):
                error_msg = validation.get("errorMessage", "Valor inválido")
                required = " (*)" if current_field.get("required") else ""
                return f"❌ {error_msg}\n\n📝 {current_field['label']}{required}"

            # Validar min/max para números
            if "min" in validation or "max" in validation:
                try:
                    value_num = float(user_input)
                    if "min" in validation and value_num < validation["min"]:
                        error_msg = validation.get("errorMessage", "Valor inválido")
                        required = " (*)" if current_field.get("required") else ""
                        return (
                            f"❌ {error_msg}\n\n📝 {current_field['label']}{required}"
                        )
                    if "max" in validation and value_num > validation["max"]:
                        error_msg = validation.get("errorMessage", "Valor inválido")
                        required = " (*)" if current_field.get("required") else ""
                        return (
                            f"❌ {error_msg}\n\n📝 {current_field['label']}{required}"
                        )
                except ValueError:
                    error_msg = validation.get("errorMessage", "Debe ser un número")
                    required = " (*)" if current_field.get("required") else ""
                    return f"❌ {error_msg}\n\n📝 {current_field['label']}{required}"

        # Guardar el valor
        field_name = current_field["name"]

        # Convertir tipo si es necesario
        if current_field.get("type") == "number":
            try:
                user_input = int(user_input)
            except:
                try:
                    user_input = float(user_input)
                except:
                    pass

        session["pendingFormData"][field_name] = user_input
        session_vars[field_name] = user_input

        # Avanzar al siguiente campo
        next_index = session["formFieldIndex"] + 1

        if next_index < len(fields):
            # Hay más campos
            session["formFieldIndex"] = next_index
            session["currentFormField"] = fields[next_index]

            next_field = fields[next_index]
            required = " (*)" if next_field.get("required") else ""

            return f"✅ Guardado.\n\n📝 {next_field['label']}{required}"
        else:
            # Formulario completado
            session["waitingForInput"] = None
            session["currentFormField"] = None
            session["formFieldIndex"] = 0

            # Procesar onSubmit si existe
            on_submit = flow.get("onSubmit")
            if on_submit:
                # Aquí se podría llamar al servicio externo
                # service = on_submit.get("service")
                # if service:
                #     call_external_service(service, session["pendingFormData"])

                session["currentFlow"] = on_submit.get("next", self.BOT["defaultFlow"])
            else:
                session["currentFlow"] = flow.get("next", self.BOT["defaultFlow"])

            session["pendingFormData"] = {}

            return self._process_flow(session, None)

    def _format_options(self, options: list, flow: dict, session_vars: dict) -> str:
        """Formatea las opciones como texto"""
        content = self.replace_variables(flow.get("content", ""), session_vars)
        options_text = "\n".join(
            [f"  {i+1}️⃣. {opt['label']}" for i, opt in enumerate(options)]
        )

        return f"{content}\n{options_text}\n\n💡 Responde con el número o nombre de la opción"

    def _format_qa(self, questions: list, flow: dict, session_vars: dict) -> str:
        """Formatea las preguntas como texto"""
        content = self.replace_variables(flow.get("content", ""), session_vars)
        questions_text = "\n".join(
            [f"  {i+1}️⃣. {q['question']}" for i, q in enumerate(questions)]
        )

        return f"{content}\n{questions_text}\n\n💡 Escribe tu pregunta"


# =====================================================
# PRUEBAS
# =====================================================


def test_chatbot():
    """Prueba el chatbot simulando una conversación"""

    print("=" * 60)
    print("PRUEBA DEL CHATBOT - MODO CONVERSACIONAL")
    print("=" * 60)

    bot = ChatBotEngine("chatbot.json")
    user_id = "test_user_123"

    def send_message(message=None, metadata=None):
        """Simula enviar un mensaje y recibir respuesta"""
        if message:
            print(f"\n👤 Usuario: {message}")
        response = bot.process_message(user_id, message, metadata)
        print(f"\n🤖 Bot:\n{response}")
        print("-" * 60)
        return response

    # Test 1: Inicio con metadata
    print("\n📍 TEST 1: Inicio de conversación")
    send_message(metadata={"usuarioNombre": "Carlos Pérez", "edad": 25})

    # Test 2: Seleccionar FAQ
    print("\n📍 TEST 2: Seleccionar FAQ")
    send_message("1")  # o "faq"

    # Test 3: Hacer una pregunta
    print("\n📍 TEST 3: Preguntar horario")
    send_message("¿Cuál es el horario de atención?")

    # Test 4: Volver al menú
    print("\n📍 TEST 4: Volver al menú")
    send_message("Volver al menú principal")

    # Test 5: Ir a registro
    print("\n📍 TEST 5: Ir a registro")
    send_message("2")  # o "registro"

    # Test 6: Completar formulario campo por campo
    print("\n📍 TEST 6: Completar formulario")
    send_message("Carlos Pérez García")
    send_message("carlos.perez@example.com")
    send_message("+51987654321")

    # Test 7: Ir a servicios
    print("\n📍 TEST 7: Consultar servicios")
    send_message("3")  # o "consultar_servicios"

    # Test 8: Ir a feedback
    print("\n📍 TEST 8: Dar feedback")
    send_message("4")  # o "feedback"

    # Test 9: Completar encuesta
    print("\n📍 TEST 9: Completar encuesta")
    send_message("5")
    send_message("Excelente servicio, muy rápido")

    print("\n✅ PRUEBAS COMPLETADAS")


if __name__ == "__main__":
    test_chatbot()
