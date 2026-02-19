// 全局变量
let currentMode = 'teaching';
let currentTaskId = null;
let tasks = [];
let currentUserId = localStorage.getItem('currentUserId') || null;
let userStorage = null; // 用户存储管理器
let isAutoLoginInProgress = false; // 防止重复显示登录弹窗

// DOM 元素
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const newTaskBtn = document.getElementById('new-task-btn');
const modeIcon = document.getElementById('mode-icon');
const modeName = document.getElementById('mode-name');
const userIdModal = document.getElementById('user-id-modal');
const userIdInput = document.getElementById('user-id-input');
const userIdConfirm = document.getElementById('user-id-confirm');
const clearAllTasksBtn = document.getElementById('clear-all-tasks-btn');
const userMenuBtn = document.getElementById('user-menu-btn');
const userDropdown = document.getElementById('user-dropdown');
const logoutBtn = document.getElementById('logout-btn');
const currentUserDisplay = document.getElementById('current-user-display');
const dropdownUserName = document.getElementById('dropdown-user-name');
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.querySelector('.sidebar');
const sidebarOverlay = document.querySelector('.sidebar-overlay');

// 控制元素
const voiceBtn = document.getElementById('voice-btn');
const attachmentBtn = document.getElementById('attachment-btn');
const toolsBtn = document.getElementById('tools-btn');
const toolsMenu = document.getElementById('tools-menu');

// 任务管理
class TaskManager {
    constructor(userStorage) {
        this.userStorage = userStorage;
        this.tasks = this.userStorage ? this.userStorage.getItem('teachingTasks', []) : [];
        this.currentTaskId = this.userStorage ? this.userStorage.getItem('currentTaskId') : null;
        this.render();
    }

    createTask(title = null) {
        const task = {
            id: Date.now().toString(),
            mode: 'teaching',
            title: title || '新教案',
            messages: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        this.tasks.unshift(task);
        this.saveToStorage();
        return task;
    }

    updateTaskTitle(taskId, title) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.title = title;
            task.updatedAt = new Date().toISOString();
            this.saveToStorage();
            this.render();
        }
    }

    addMessage(taskId, role, content) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.messages.push({ role, content, timestamp: new Date().toISOString() });
            task.updatedAt = new Date().toISOString();

            // 自动更新任务标题（使用第一条用户消息）
            if (role === 'user' && task.messages.filter(m => m.role === 'user').length === 1) {
                task.title = content.slice(0, 30) + (content.length > 30 ? '...' : '');
            }

            this.saveToStorage();
            this.render();
        }
    }

    getLastAiMessageText(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task || !task.messages || task.messages.length === 0) return null;
        for (let i = task.messages.length - 1; i >= 0; i--) {
            const msg = task.messages[i];
            if (msg && msg.role === 'ai' && typeof msg.content === 'string' && msg.content.length > 0) {
                return msg.content;
            }
        }
        return null;
    }

    getTask(taskId) {
        return this.tasks.find(t => t.id === taskId);
    }

    deleteTask(taskId) {
        const wasCurrent = currentTaskId === taskId;
        this.tasks = this.tasks.filter(t => t.id !== taskId);
        this.saveToStorage();
        this.render();

        if (wasCurrent) {
            if (this.tasks.length > 0) {
                const nextTask = this.tasks[0];
                this.switchToTask(nextTask.id);
            } else {
                createNewTask();
            }
        }
    }

    clearAllTasks() {
        this.tasks = [];
        currentTaskId = null;
        this.saveToStorage();
        this.render();
        chatWindow.innerHTML = '';
        createNewTask();
    }

    saveToStorage() {
        if (this.userStorage) {
            this.userStorage.setItem('teachingTasks', this.tasks);
            if (currentTaskId) {
                this.userStorage.setItem('currentTaskId', currentTaskId);
            }
        }
    }

    render() {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

        const todayTasks = [];
        const yesterdayTasks = [];
        const weekTasks = [];

        this.tasks.forEach(task => {
            const taskDate = new Date(task.updatedAt);
            const taskDay = new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate());

            if (taskDay.getTime() === today.getTime()) {
                todayTasks.push(task);
            } else if (taskDay.getTime() === yesterday.getTime()) {
                yesterdayTasks.push(task);
            } else if (taskDate >= weekAgo) {
                weekTasks.push(task);
            }
        });

        this.renderTaskSection('today-tasks', todayTasks);
        this.renderTaskSection('yesterday-tasks', yesterdayTasks);
        this.renderTaskSection('week-tasks', weekTasks);
    }

    renderTaskSection(containerId, tasks) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = `task-item ${task.id === currentTaskId ? 'active' : ''}`;
            taskElement.innerHTML = `
                <i class="fas fa-graduation-cap"></i>
                <span class="task-title">${task.title}</span>
                <button type="button" class="task-delete-btn" title="删除教案" aria-label="删除教案">
                    <i class="fas fa-trash"></i>
                </button>
            `;

            taskElement.addEventListener('click', () => {
                this.switchToTask(task.id);
            });

            const deleteBtn = taskElement.querySelector('.task-delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const ok = window.confirm('确认删除该教案？此操作不可恢复');
                if (!ok) return;
                this.deleteTask(task.id);
            });

            container.appendChild(taskElement);
        });
    }

    switchToTask(taskId) {
        const task = this.getTask(taskId);
        if (!task) return;

        currentTaskId = taskId;

        this.render();
        this.loadTaskMessages(task);

        if (this.userStorage) {
            this.userStorage.setItem('currentTaskId', currentTaskId);
        }
    }

    loadTaskMessages(task) {
        chatWindow.innerHTML = '';

        if (task.messages.length === 0) {
            this.showWelcomeMessage();
        } else {
            task.messages.forEach(msg => {
                this.appendMessage(msg.role, msg.content);
            });
        }
    }

    showWelcomeMessage() {
        const welcomeMessage = '欢迎使用智能教案与PPT生成系统！👋\n\n请输入您的教学主题、教学目标、教学对象等信息，系统将自动为您生成详细的教案和相应的教学PPT。\n\n例如：\n• "为高中一年级学生生成关于光学的教案和PPT"\n• "创建初中数学一次函数的教学课件"';

        this.appendMessage('ai', welcomeMessage);
    }

    appendMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        if (role === 'ai') {
            messageContent.innerHTML = this.renderMarkdown(content);
        } else {
            messageContent.textContent = content;
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    renderMarkdown(mdText) {
        if (!mdText) return '';
        try {
            const md = window.markdownit({
                html: false,
                linkify: true,
                typographer: true,
                breaks: true
            });
            const dirty = md.render(mdText);
            const clean = window.DOMPurify ? window.DOMPurify.sanitize(dirty, {USE_PROFILES: {html: true}}) : dirty;
            return `<div class="md">${clean}</div>`;
        } catch (e) {
            console.error('Markdown 渲染失败:', e);
            return `<div class="md"><pre>${mdText}</pre></div>`;
        }
    }
}

// 初始化任务管理器
let taskManager = null;

// 用户ID管理
function showUserIdModal() {
    if (isAutoLoginInProgress) {
        console.log('🚫 自动登录进行中，跳过显示登录弹窗');
        return;
    }

    console.log('🔑 显示登录弹窗');
    clearUIForLogin();
    userIdModal.classList.remove('hidden');
    userIdInput.focus();
}

function clearUIForLogin() {
    chatWindow.innerHTML = '';
    currentUserDisplay.textContent = '';
    dropdownUserName.textContent = '';
    document.getElementById('today-tasks').innerHTML = '';
    document.getElementById('yesterday-tasks').innerHTML = '';
    document.getElementById('week-tasks').innerHTML = '';
}

function hideUserIdModal() {
    userIdModal.classList.add('hidden');
}

function setUserId(userId) {
    console.log('🔧 设置用户ID:', userId);

    currentUserId = userId;
    localStorage.setItem('currentUserId', userId);

    userStorage = new UserStorage(userId);
    taskManager = new TaskManager(userStorage);

    console.log('✅ 用户ID已设置:', userId);
    console.log('📊 用户存储空间大小:', (userStorage.getDataSize() / 1024).toFixed(2) + ' KB');

    updateUserDisplay();
}

function updateUserDisplay() {
    if (currentUserId) {
        currentUserDisplay.textContent = currentUserId.length > 8 ? currentUserId.substring(0, 8) + '...' : currentUserId;
        dropdownUserName.textContent = currentUserId;
    }
}

function showAutoLoginMessage(userId) {
    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: 14px;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    message.textContent = `欢迎回来，${userId}！`;

    document.body.appendChild(message);

    setTimeout(() => message.style.opacity = '1', 100);

    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => document.body.removeChild(message), 300);
    }, 3000);
}

function logout() {
    localStorage.removeItem('currentUserId');
    currentUserId = null;
    userStorage = null;
    taskManager = null;

    showUserIdModal();
}

// 事件监听器
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 页面加载完成，检查用户登录状态...');

    const storedUserId = localStorage.getItem('currentUserId');
    console.log('🔍 localStorage中的用户ID:', storedUserId);

    if (!storedUserId || storedUserId.trim() === '') {
        console.log('❌ 未找到有效的缓存用户ID，显示登录弹窗');
        showUserIdModal();
        return;
    }

    console.log('✅ 找到缓存的用户ID:', storedUserId);
    isAutoLoginInProgress = true;

    currentUserId = storedUserId;

    console.log('🔄 开始自动登录流程...');
    setUserId(currentUserId);
    updateUserDisplay();

    console.log('🚀 直接初始化应用组件...');
    initializeAppComponents();

    showAutoLoginMessage(currentUserId);

    hideUserIdModal();

    isAutoLoginInProgress = false;
    console.log('✅ 自动登录完成');
});

function initializeAppComponents() {
    console.log('🎯 初始化应用组件...');

    currentTaskId = userStorage.getItem('currentTaskId');
    console.log('📋 当前任务ID:', currentTaskId);

    if (currentTaskId) {
        const task = taskManager.getTask(currentTaskId);
        if (task) {
            console.log('🔄 切换到现有任务:', currentTaskId);
            taskManager.switchToTask(currentTaskId);
        } else {
            console.log('📝 创建新任务（旧任务不存在）');
            createNewTask();
        }
    } else {
        console.log('📝 创建新任务（无当前任务）');
        createNewTask();
    }

    initializeControls();
}

function initializeApp() {
    console.log('🔧 初始化应用...');

    if (!userStorage || !taskManager) {
        if (currentUserId) {
            console.log('🔧 重新初始化用户存储和任务管理器');
            setUserId(currentUserId);
        } else {
            console.log('❌ 没有用户ID，显示登录弹窗');
            showUserIdModal();
            return;
        }
    }

    initializeAppComponents();
}

// 新任务按钮
newTaskBtn.addEventListener('click', () => {
    createNewTask();
});

// 用户ID弹窗事件监听
userIdConfirm.addEventListener('click', () => {
    const userId = userIdInput.value.trim();
    if (!userId) {
        alert('请输入用户ID');
        return;
    }

    console.log('用户登录:', userId);
    setUserId(userId);
    hideUserIdModal();
    initializeApp();
});

userIdInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        userIdConfirm.click();
    }
});

// 聊天表单提交
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    if (!currentTaskId || !taskManager) {
        createNewTask();
    }

    if (taskManager) {
        taskManager.addMessage(currentTaskId, 'user', text);
        taskManager.appendMessage('user', text);
    }
    userInput.value = '';

    try {
        const response = await fetch('/send_message_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                task_id: currentTaskId,
                user_id: currentUserId
            })
        });

        const aiMessageDiv = document.createElement('div');
        aiMessageDiv.className = 'message ai';
        aiMessageDiv.innerHTML = `
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="streaming-content"></div>
                <span class="cursor"></span>
            </div>
        `;
        chatWindow.appendChild(aiMessageDiv);
        const streamingContent = aiMessageDiv.querySelector('.streaming-content');
        const cursor = aiMessageDiv.querySelector('.cursor');

        let fullResponse = '';

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.type === 'token') {
                            fullResponse += data.content;

                            if (taskManager) {
                                streamingContent.innerHTML = taskManager.renderMarkdown(fullResponse);
                            } else {
                                streamingContent.textContent = fullResponse;
                            }
                            chatWindow.scrollTop = chatWindow.scrollHeight;
                        } else if (data.type === 'done') {
                            cursor.remove();

                            if (!fullResponse && data.response) {
                                fullResponse = data.response;
                                if (taskManager) {
                                    streamingContent.innerHTML = taskManager.renderMarkdown(fullResponse);
                                } else {
                                    streamingContent.textContent = fullResponse;
                                }
                            }

                            if (taskManager) {
                                taskManager.addMessage(currentTaskId, 'ai', fullResponse);
                            }
                        } else if (data.type === 'error') {
                            cursor.remove();
                            streamingContent.textContent = '抱歉，发生了错误：' + data.message;
                        }
                    } catch (e) {
                        console.error('解析SSE数据错误:', e);
                    }
                }
            }
        }

    } catch (error) {
        console.error('Error:', error);

        if (taskManager) {
            taskManager.appendMessage('ai', '抱歉，发生了错误，请稍后重试。');
        }
    }
});

function createNewTask(title = null) {
    if (!taskManager) {
        if (currentUserId) {
            setUserId(currentUserId);
        } else {
            console.error('无法创建任务：用户未登录');
            return;
        }
    }

    const task = taskManager.createTask(title);
    currentTaskId = task.id;

    taskManager.switchToTask(currentTaskId);
}

// 清理所有任务按钮事件
if (clearAllTasksBtn) {
    clearAllTasksBtn.addEventListener('click', () => {
        const confirmed = confirm('确定要清理所有任务吗？此操作不可恢复。');
        if (confirmed && taskManager) {
            taskManager.clearAllTasks();
        }
    });
}

// 用户菜单事件
if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!userDropdown.contains(e.target) && !userMenuBtn.contains(e.target)) {
            userDropdown.classList.add('hidden');
        }
    });
}

// 退出登录按钮事件
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        const confirmed = confirm('确定要退出登录吗？');
        if (confirmed) {
            logout();
            if (userDropdown) {
                userDropdown.classList.add('hidden');
            }
        }
    });
}

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createNewTask();
    }
});

// 移动端侧边栏控制
function toggleSidebar() {
    sidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('active');

    const icon = menuToggle.querySelector('i');
    if (sidebar.classList.contains('open')) {
        icon.className = 'fas fa-times';
    } else {
        icon.className = 'fas fa-bars';
    }
}

function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('active');
    const icon = menuToggle.querySelector('i');
    icon.className = 'fas fa-bars';
}

if (menuToggle) {
    menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleSidebar();
    });
}

if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeSidebar);
}

const originalSwitchToTask = TaskManager.prototype.switchToTask;
TaskManager.prototype.switchToTask = function(taskId) {
    originalSwitchToTask.call(this, taskId);

    if (window.innerWidth <= 768) {
        closeSidebar();
    }
};

let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
            const icon = menuToggle.querySelector('i');
            if (icon) icon.className = 'fas fa-bars';
        }
    }, 250);
});

document.addEventListener('touchmove', (e) => {
    if (sidebar.classList.contains('open') && !sidebar.contains(e.target)) {
        e.preventDefault();
    }
}, { passive: false });

// 初始化控制元素
function initializeControls() {
    console.log('🎛️ 初始化控制元素...');

    if (toolsBtn && toolsMenu) {
        toolsBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            toolsMenu.classList.toggle('hidden');
        });

        document.addEventListener('click', function() {
            if (toolsMenu && !toolsMenu.classList.contains('hidden')) {
                toolsMenu.classList.add('hidden');
            }
        });

        toolsMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    if (voiceBtn) {
        voiceBtn.addEventListener('click', function() {
            console.log('🎤 语音输入功能（待实现）');
            showToast('语音输入功能正在开发中...', 'info');
        });
    }

    if (attachmentBtn) {
        attachmentBtn.addEventListener('click', function() {
            console.log('📎 附件功能（待实现）');
            showToast('附件功能正在开发中...', 'info');
        });
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? '#4CAF50' : '#2196F3',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '6px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        zIndex: '10000',
        fontSize: '14px',
        fontWeight: '500',
        opacity: '0',
        transform: 'translateY(-10px)',
        transition: 'all 0.3s ease'
    });

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

