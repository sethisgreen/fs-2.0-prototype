# FamilySearch fs-js-lite SDK Integration Plan

## 🎯 **Overview**

The [FamilySearch fs-js-lite SDK](https://github.com/FamilySearch/fs-js-lite) is the official JavaScript SDK for the FamilySearch API. This document outlines how we can integrate it into our FS Agent project to simplify API interactions and improve reliability.

## ✅ **Benefits of Using fs-js-lite**

### **1. Official SDK**

- Maintained by FamilySearch
- Regular updates and bug fixes
- Community support and documentation

### **2. Simplified Authentication**

- Built-in OAuth 2.0 flow handling
- Automatic token management
- Cookie-based session persistence

### **3. Robust Error Handling**

- Network error detection
- HTTP error classification
- Automatic retry for throttled requests

### **4. Middleware Support**

- Request/response middleware
- Caching capabilities
- Logging and monitoring

### **5. GEDCOM X Integration**

- Optional structured data objects
- Better data type safety
- Easier data manipulation

## 🔧 **Integration Strategy**

### **Phase 1: SDK Setup**

#### **1.1 Install SDK**

```bash
# For Node.js backend
npm install --save fs-js-lite

# For browser frontend
<script src="https://unpkg.com/fs-js-lite@latest/dist/FamilySearch.min.js"></script>
```

#### **1.2 Initialize SDK**

```javascript
// Backend initialization (Node.js)
const FamilySearch = require("fs-js-lite");

const fs = new FamilySearch({
  environment: "production",
  appKey: process.env.FAMILYSEARCH_CLIENT_ID,
  redirectUri: "https://fs-agent.com/oauth/callback",
  accessToken: process.env.FAMILYSEARCH_ACCESS_TOKEN,
});
```

### **Phase 2: Replace Manual API Calls**

#### **2.1 Collections API**

```javascript
// Current manual approach:
const response = await fetch(
  "https://api.familysearch.org/platform/collections",
  {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/x-gedcomx-v1+json",
    },
  }
);

// With fs-js-lite:
fs.get("/platform/collections", function (error, response) {
  if (error) {
    console.error("Network error:", error);
  } else if (response.statusCode >= 400) {
    console.error("HTTP error:", response.statusCode);
  } else {
    console.log("Collections:", response.data);
  }
});
```

#### **2.2 Places Search**

```javascript
// With fs-js-lite:
fs.get(
  "/platform/places/search?q=New%20York&count=5",
  {
    headers: {
      Accept: "application/json",
    },
  },
  function (error, response) {
    if (error) {
      console.error("Search error:", error);
    } else {
      console.log("Places found:", response.data);
    }
  }
);
```

### **Phase 3: Enhanced Features**

#### **3.1 Middleware for Caching**

```javascript
// Add caching middleware
fs.addResponseMiddleware(function (client, request, response, next) {
  if (response.statusCode === 200) {
    // Cache successful responses
    cache.set(request.url, response.data);
  }
  next();
});
```

#### **3.2 Logging Middleware**

```javascript
// Add logging middleware
fs.addRequestMiddleware(function (client, request, next) {
  console.log(`[${new Date().toISOString()}] ${request.method} ${request.url}`);
  next();
});
```

#### **3.3 Error Handling Middleware**

```javascript
// Add error handling middleware
fs.addResponseMiddleware(function (client, request, response, next) {
  if (response.statusCode >= 400) {
    console.error(`API Error: ${response.statusCode} - ${response.statusText}`);
  }
  next();
});
```

## 📋 **Implementation Plan**

### **Step 1: Backend Integration**

1. Install fs-js-lite in our Python backend
2. Create a JavaScript bridge for API calls
3. Replace manual HTTP requests with SDK calls
4. Add middleware for caching and logging

### **Step 2: Frontend Integration**

1. Include SDK in our landing page
2. Create client-side API wrapper
3. Implement OAuth flow using SDK
4. Add error handling and user feedback

### **Step 3: Enhanced Features**

1. Implement caching middleware
2. Add comprehensive logging
3. Create structured error handling
4. Integrate with our MCP server architecture

## 🚀 **Benefits for FS Agent**

### **1. Reliability**

- Built-in retry logic for throttled requests
- Automatic error handling
- Network error detection

### **2. Maintainability**

- Official SDK with regular updates
- Better documentation and examples
- Community support

### **3. Performance**

- Built-in caching capabilities
- Optimized request handling
- Middleware for custom optimizations

### **4. Developer Experience**

- Simplified API calls
- Better error messages
- Structured data objects (optional)

## 📊 **Migration Strategy**

### **Current State**

- Manual HTTP requests with httpx
- Custom OAuth implementation
- Basic error handling

### **Target State**

- fs-js-lite SDK for all API calls
- Built-in OAuth flow
- Comprehensive error handling
- Middleware for caching and logging

### **Migration Steps**

1. **Week 1**: Install and test SDK
2. **Week 2**: Replace collections and places API calls
3. **Week 3**: Add middleware and error handling
4. **Week 4**: Integrate with MCP server architecture

## 🎯 **Next Steps**

### **Immediate Actions**

1. **Test SDK Installation** - Verify SDK works in our environment
2. **Compare API Results** - Ensure SDK returns same data as manual calls
3. **Performance Testing** - Compare performance with current implementation

### **Development Tasks**

1. **Create SDK Wrapper** - Build a Python wrapper for the JavaScript SDK
2. **Update Server Code** - Replace manual API calls with SDK calls
3. **Add Middleware** - Implement caching and logging middleware
4. **Update Documentation** - Document new API usage patterns

### **Testing Strategy**

1. **Unit Tests** - Test SDK integration
2. **Integration Tests** - Test with real FamilySearch API
3. **Performance Tests** - Compare with current implementation
4. **Error Handling Tests** - Test various error scenarios

## 💡 **Conclusion**

The fs-js-lite SDK would significantly improve our FS Agent project by:

- **Simplifying API interactions** with built-in methods
- **Improving reliability** with automatic retry and error handling
- **Enhancing maintainability** with official SDK support
- **Adding features** like caching and middleware support

This integration would be a valuable upgrade to our current manual API implementation.
