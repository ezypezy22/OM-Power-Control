import Foundation
import Security

/// The amplifier's admin password, kept in the macOS login Keychain. Only the page's own bridge calls this;
/// the password is never written to settings, logs or traces.
struct AdminKeychain {
    var service = "com.grmi64.OM3501AControl.admin-password"
    private let account = "admin"
    private var base: [String: Any] {
        [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service, kSecAttrAccount as String: account]
    }
    /// Same rule the amplifier and the engine enforce: 1 to 10 printable ASCII characters, no semicolon.
    static func valid(_ password: String) -> Bool {
        let scalars = password.unicodeScalars
        return (1...10).contains(scalars.count) && scalars.allSatisfy { $0.value >= 33 && $0.value <= 126 && $0 != ";" }
    }
    func read() -> String? {
        var query = base
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var item: CFTypeRef?
        guard SecItemCopyMatching(query as CFDictionary, &item) == errSecSuccess, let data = item as? Data,
              let text = String(data: data, encoding: .utf8), Self.valid(text) else { return nil }
        return text
    }
    @discardableResult func save(_ password: String) -> Bool {
        guard Self.valid(password), let data = password.data(using: .utf8) else { return false }
        SecItemDelete(base as CFDictionary)
        var item = base
        item[kSecValueData as String] = data
        item[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        return SecItemAdd(item as CFDictionary, nil) == errSecSuccess
    }
    @discardableResult func delete() -> Bool {
        let status = SecItemDelete(base as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }
}
