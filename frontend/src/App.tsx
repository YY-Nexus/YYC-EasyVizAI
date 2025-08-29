import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Typography, Button, Card, Row, Col } from 'antd';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph } = Typography;

// 健康检查组件
const HealthCheck: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <Card>
        <Title level={3}>系统健康状态</Title>
        <Paragraph>
          系统运行正常，所有服务已启动。
        </Paragraph>
      </Card>
    </div>
  );
};

// 主页组件
const HomePage: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <Title level={2}>欢迎使用 YYC³ EasyVizAI</Title>
            <Paragraph>
              这是一个智能可视化平台，提供强大的数据分析和可视化功能。
            </Paragraph>
            <Button type="primary" size="large">
              开始使用
            </Button>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="数据分析">
            <Paragraph>
              智能数据分析和处理功能
            </Paragraph>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="可视化">
            <Paragraph>
              丰富的图表和可视化组件
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ 
          position: 'fixed', 
          zIndex: 1, 
          width: '100%',
          display: 'flex',
          alignItems: 'center'
        }}>
          <div style={{ color: 'white', fontSize: '18px', fontWeight: 'bold' }}>
            YYC³ EasyVizAI
          </div>
        </Header>
        <Content style={{ padding: '0 50px', marginTop: 64 }}>
          <div style={{ 
            background: '#fff', 
            padding: 24, 
            minHeight: 380,
            marginTop: 16
          }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/health" element={<HealthCheck />} />
            </Routes>
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          YYC³ EasyVizAI ©2024 Created by YY-Nexus
        </Footer>
      </Layout>
    </Router>
  );
};

export default App;