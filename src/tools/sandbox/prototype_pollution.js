/**
 * Deep merge utility for configuration objects.
 * Vulnerability: Prototype pollution via __proto__ assignment (CWE-1321).
 */
function mergeConfigs(target, source) {
    for (let key in source) {
        if (source.hasOwnProperty(key)) {
            // Line 9: Assigning keys without sanitizing __proto__ or constructor polluting Object.prototype
            if (typeof source[key] === 'object' && source[key] !== null) {
                if (!target[key]) target[key] = {};
                mergeConfigs(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
    }
    return target;
}

module.exports = { mergeConfigs };
