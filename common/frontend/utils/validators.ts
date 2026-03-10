/**
 * 验证工具函数库
 * Common validation utilities for frontend applications
 */

// Email validation
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Password strength validation
export const isStrongPassword = (password: string): boolean => {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  return passwordRegex.test(password);
};

// URL validation
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Phone number validation (basic)
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
  return phoneRegex.test(phone);
};

// Required field validation
export const isRequired = (value: any): boolean => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined;
};

// Length validation
export const hasValidLength = (value: string, min: number, max?: number): boolean => {
  const length = value.length;
  if (max !== undefined) {
    return length >= min && length <= max;
  }
  return length >= min;
};

// Numeric validation
export const isNumeric = (value: string): boolean => {
  return !isNaN(Number(value)) && !isNaN(parseFloat(value));
};

// Date validation
export const isValidDate = (dateString: string): boolean => {
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date.getTime());
};

// Form validation helper
export interface ValidationRule {
  validator: (value: any) => boolean;
  message: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export const validateField = (value: any, rules: ValidationRule[]): ValidationResult => {
  const errors: string[] = [];
  
  for (const rule of rules) {
    if (!rule.validator(value)) {
      errors.push(rule.message);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Common validation rules
export const ValidationRules = {
  required: (message = '此字段为必填项'): ValidationRule => ({
    validator: isRequired,
    message
  }),
  
  email: (message = '请输入有效的邮箱地址'): ValidationRule => ({
    validator: isValidEmail,
    message
  }),
  
  strongPassword: (message = '密码必须包含至少8个字符，包括大小写字母、数字和特殊字符'): ValidationRule => ({
    validator: isStrongPassword,
    message
  }),
  
  minLength: (min: number, message?: string): ValidationRule => ({
    validator: (value: string) => hasValidLength(value, min),
    message: message || `最少需要${min}个字符`
  }),
  
  maxLength: (max: number, message?: string): ValidationRule => ({
    validator: (value: string) => hasValidLength(value, 0, max),
    message: message || `最多允许${max}个字符`
  }),
  
  numeric: (message = '请输入有效的数字'): ValidationRule => ({
    validator: isNumeric,
    message
  }),
  
  url: (message = '请输入有效的URL'): ValidationRule => ({
    validator: isValidUrl,
    message
  }),
  
  phone: (message = '请输入有效的电话号码'): ValidationRule => ({
    validator: isValidPhone,
    message
  })
};

export default {
  isValidEmail,
  isStrongPassword,
  isValidUrl,
  isValidPhone,
  isRequired,
  hasValidLength,
  isNumeric,
  isValidDate,
  validateField,
  ValidationRules
};