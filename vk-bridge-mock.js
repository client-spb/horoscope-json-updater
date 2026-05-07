/////////////////////
// ==================== MOCK VK BRIDGE (для локалки) ====================
const IS_LOCAL = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

if (IS_LOCAL) {
    console.log('🧪 Режим разработки: используем мок VK Bridge');
    
    // Мок-данные пользователя
    const mockUser = {
        id: 123456789,
        first_name: 'Иван',
        last_name: 'Иванов',
        photo_100: 'https://i.pravatar.cc/100?img=12',
        city: { title: 'Москва' },
        country: { title: 'Россия' }
    };
    
    // Мок-хранилище
    const mockStorage = {};
    
    // Переопределяем vkBridge.send
    if (window.vkBridge) {
        const originalSend = window.vkBridge.send;
        window.vkBridge.send = async function(method, props) {
            console.log(`🔧 [MOCK] vkBridge.send('${method}')`, props);
            
            switch(method) {
                case 'VKWebAppInit':
                    return { result: true };
                    
                case 'VKWebAppGetUserInfo':
                    return mockUser;
                    
                case 'VKWebAppStorageGet':
                    const keys = props?.keys || [];
                    return { 
                        keys: keys.map(k => ({ 
                            key: k, 
                            value: mockStorage[k] || null 
                        })) 
                    };
                    
                case 'VKWebAppStorageSet':
                    mockStorage[props.key] = props.value;
                    console.log(`💾 [MOCK] Сохранено: ${props.key} = ${props.value}`);
                    return { result: true };
                    
                case 'VKWebAppShowNativeAds':
                case 'VKWebAppCheckNativeAds':
                    return { result: true, ads: [] };
                    
                default:
                    console.warn(`⚠️ [MOCK] Метод '${method}' не замокан`);
                    return { result: true };
            }
        };
        
        // Мок подписки на события
        window.vkBridge.subscribe = function(callback) {
            console.log('🔔 [MOCK] Подписка на события:', callback);
            // Можно эмулировать события вручную для тестов:
            // callback({ detail: { type: 'VKWebAppAdsResult', data: { reward: 100 } } });
        };
    }
}
/////////////////////