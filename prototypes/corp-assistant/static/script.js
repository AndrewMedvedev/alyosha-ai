// Telegram WebApp инициализация
const tg = window.Telegram.WebApp;
tg.expand();
tg.ready();

// Глобальные переменные
let selectedFiles = [];
const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024; // 2ГБ
const SUPPORTED_EXTENSIONS = ["pdf", "docx", "xlsx", "pptx"];
// Укажите полный URL вашего бэкенда
const API_ENDPOINT =
  "https://9a56d20f142c.ngrok-free.app/api/v1/documents/upload";

// Элементы DOM
const step1 = document.getElementById("step1");
const step2 = document.getElementById("step2");
const stepLineFill = document.getElementById("stepLineFill");
const stepContent1 = document.getElementById("stepContent1");
const progressContainer = document.getElementById("progressContainer");
const fileInput = document.getElementById("fileInput");
const uploadArea = document.getElementById("uploadArea");
const fileList = document.getElementById("fileList");
const uploadBtn = document.getElementById("uploadBtn");
const errorMessage = document.getElementById("errorMessage");
const progressFill = document.getElementById("progressFill");
const successMessage = document.getElementById("successMessage");

// Инициализация
function init() {
  setupEventListeners();
  resetForm();
}

// Настройка обработчиков событий
function setupEventListeners() {
  // Клик по области загрузки
  uploadArea.addEventListener("click", () => fileInput.click());

  // Выбор файлов через input
  fileInput.addEventListener("change", handleFileSelect);

  // Drag and Drop
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.add("drag-over");
  });

  uploadArea.addEventListener("dragleave", (e) => {
    e.preventDefault();
    e.stopPropagation();
    // Проверяем, что мы действительно вышли из области
    if (!uploadArea.contains(e.relatedTarget)) {
      uploadArea.classList.remove("drag-over");
    }
  });

  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove("drag-over");
    if (e.dataTransfer.files.length) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  });

  // Закрытие сообщения об ошибке при клике
  errorMessage.addEventListener("click", () => {
    errorMessage.style.display = "none";
  });
}

// Обработка выбора файлов через input
function handleFileSelect(e) {
  handleFiles(Array.from(e.target.files));
  fileInput.value = ""; // Сброс input
}

// Основная обработка файлов
function handleFiles(files) {
  errorMessage.style.display = "none";
  errorMessage.textContent = "";

  const newFiles = Array.from(files);
  const validFiles = [];
  const errors = [];

  // Проверка каждого файла
  newFiles.forEach((file) => {
    const fileExtension = file.name.split(".").pop().toLowerCase();

    // Проверка расширения
    if (!SUPPORTED_EXTENSIONS.includes(fileExtension)) {
      errors.push(`"${file.name}" - неподдерживаемый формат`);
      return;
    }

    // Проверка размера
    if (file.size > MAX_FILE_SIZE) {
      errors.push(`"${file.name}" - превышает 2 ГБ`);
      return;
    }

    // Проверка на дубликаты
    if (
      selectedFiles.some((f) => f.name === file.name && f.size === file.size)
    ) {
      errors.push(`"${file.name}" - уже добавлен`);
      return;
    }

    validFiles.push(file);
  });

  // Показываем ошибки, если есть
  if (errors.length > 0) {
    showError(`Некоторые файлы не добавлены:<br>${errors.join("<br>")}`);
  }

  if (validFiles.length === 0) return;

  // Добавляем файлы
  selectedFiles = [...selectedFiles, ...validFiles];
  renderFileList();
  updateUploadButton();
}

// Отображение списка файлов
function renderFileList() {
  fileList.innerHTML = "";

  if (selectedFiles.length === 0) {
    fileList.style.display = "none";
    return;
  }

  fileList.style.display = "block";

  selectedFiles.forEach((file, index) => {
    const fileElement = document.createElement("div");
    fileElement.className = "file-item";

    const sizeGB = (file.size / (1024 * 1024 * 1024)).toFixed(2);

    fileElement.innerHTML = `
          <div class="file-info">
            <div class="file-name">${escapeHtml(file.name)}</div>
            <div class="file-size">${sizeGB} ГБ</div>
          </div>
          <button class="remove-btn" onclick="removeFile(${index})" title="Удалить">×</button>
        `;

    fileList.appendChild(fileElement);
  });
}

// Экранирование HTML
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Удаление файла
function removeFile(index) {
  selectedFiles.splice(index, 1);
  renderFileList();
  updateUploadButton();
}

// Обновление состояния кнопки загрузки
function updateUploadButton() {
  uploadBtn.disabled = selectedFiles.length === 0;
  uploadBtn.textContent =
    selectedFiles.length > 0
      ? `Загрузить файлы (${selectedFiles.length})`
      : "Загрузить файлы";
}

// Показать ошибку
function showError(message) {
  errorMessage.innerHTML = message;
  errorMessage.style.display = "block";

  // Автоматически скрыть через 7 секунд
  setTimeout(() => {
    if (errorMessage.style.display === "block") {
      errorMessage.style.display = "none";
    }
  }, 7000);
}

// Отправка файлов на сервер
async function uploadFiles() {
  if (selectedFiles.length === 0) return;

  // Получаем Telegram ID пользователя
  const telegramUserId =
    tg.initDataUnsafe?.user?.id ||
    tg.initDataUnsafe?.user_id ||
    tg.initData?.user?.id;

  if (!telegramUserId) {
    showError(
      "Не удалось получить ID пользователя Telegram. Пожалуйста, откройте через Telegram бота.",
    );
    return;
  }

  // Переход ко второму шагу
  step1.classList.remove("active");
  step2.classList.add("active");
  stepLineFill.style.width = "100%";
  stepContent1.classList.remove("active");
  progressContainer.classList.add("active");

  // Показываем прогресс-бар
  progressFill.style.width = "30%";
  successMessage.style.display = "none";

  try {
    // Создаем FormData
    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    // Отправляем запрос
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: {
        "X-User-ID": telegramUserId.toString(),
        // Не добавляем Content-Type - браузер сам установит с boundary
      },
      body: formData,
    });

    // Обновляем прогресс
    progressFill.style.width = "70%";

    // Проверяем статус ответа
    if (response.status === 201) {
      // Успешная загрузка
      progressFill.style.width = "100%";
      setTimeout(() => {
        successMessage.style.display = "block";
      }, 500);
    } else if (response.status === 403) {
      throw new Error("Доступ запрещен. Требуются права администратора.");
    } else if (response.status === 400) {
      throw new Error("Отсутствует заголовок X-User-ID");
    } else {
      // Пытаемся получить детальную ошибку с сервера
      let errorText = `Ошибка сервера: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorText = errorData.detail;
        }
      } catch (e) {
        // Если не получилось распарсить JSON, используем общий текст
      }
      throw new Error(errorText);
    }
  } catch (error) {
    console.error("Upload error:", error);

    // Возвращаем на первый шаг и показываем ошибку
    step1.classList.add("active");
    step2.classList.remove("active");
    stepLineFill.style.width = "50%";
    stepContent1.classList.add("active");
    progressContainer.classList.remove("active");

    showError(
      error.message ||
        "Произошла ошибка при загрузке файлов. Проверьте подключение к интернету.",
    );
  }
}

// Сброс формы
function resetForm() {
  selectedFiles = [];
  fileInput.value = "";
  fileList.innerHTML = "";
  fileList.style.display = "none";
  uploadBtn.disabled = true;
  uploadBtn.textContent = "Загрузить файлы";

  // Сброс шагов
  step1.classList.add("active");
  step2.classList.remove("active");
  stepLineFill.style.width = "50%";
  stepContent1.classList.add("active");
  progressContainer.classList.remove("active");
  successMessage.style.display = "none";
  progressFill.style.width = "0%";

  errorMessage.style.display = "none";
  errorMessage.textContent = "";
}

// Запуск при загрузке страницы
document.addEventListener("DOMContentLoaded", init);

// Экспортируем функции в глобальную область видимости
window.uploadFiles = uploadFiles;
window.resetForm = resetForm;
window.removeFile = removeFile;
