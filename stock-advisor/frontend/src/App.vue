<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" style="background: #1a1a2e; color: #eee">
      <div style="padding: 20px 16px; font-size: 18px; font-weight: bold; border-bottom: 1px solid #333">
        📈 股票顾问
      </div>
      <el-menu
        :default-active="route.path"
        background-color="#1a1a2e"
        text-color="#ccc"
        active-text-color="#409EFF"
        router
        style="border-right: none"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/signals">
          <el-icon><Bell /></el-icon>
          <span>信号中心</span>
        </el-menu-item>
        <el-menu-item index="/strategy">
          <el-icon><Setting /></el-icon>
          <span>策略配置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>
