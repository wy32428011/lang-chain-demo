import {useEffect, useState} from 'react'
import {
    Box,
    Button, Chip,
    Container,
    Divider,
    Input,
    LinearProgress,
    Tab,
    Tabs,
    Typography
} from "@mui/material";
import axios from "axios";
import ReactMarkdown from 'react-markdown';
import Sidebar from './components/Sidebar';
import AnalysisResults from './components/AnalysisResults';


function App() {
    // const [select1, setSelect1] = useState('option1');
    // const [select2, setSelect2] = useState('optionA');
    const [stockCode, setStockCode] = useState('');
    const [tabValue, setTabValue] = useState(0);
    const [tabData1, setTabData1] = useState('暂无信息');
    const [tabData2, setTabData2] = useState('暂无信息');
    const [tabData3, setTabData3] = useState('暂无信息');
    const [tabData4, setTabData4] = useState('暂无信息');
    const [tabData5, setTabData5] = useState('暂无信息');
    const [tabData6, setTabData6] = useState('暂无信息');
    const [tabData7, setTabData7] = useState('暂无信息');
    const [action, setAction] = useState('');
    const [name, setName] = useState('');
    const [currentPrice, setCurrentPrice] = useState(0.0);
    const [targetPrice, setTargetPrice] = useState('暂无信息');
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState('analysis'); // 'analysis' | 'results'
    const getData = async () => {
        setLoading(true);
        try {
            console.log(
                // 'select1:', select1,
                // 'select2:', select2,
                'stockCode:', stockCode
            )
            const res = await axios.post('/api/stock/agent', {
                symbol: stockCode,
            });
            const data = await res.data;
            console.log(data);
            setTabData1(data.price_trend_analysis);
            setTabData2(data.technical_indicators);
            setTabData3(data.news_sentiment_analysis);
            setTabData4(data.weekly_forecast);
            setTabData5(data.risk_assessment);
            setTabData6(data.operation_recommendation);
            setTabData7(data.comprehensive_conclusion);
            setName(data.name);
            setAction(data.risk_level);
            setCurrentPrice(data.current_price);
            setTargetPrice(data.target_price);
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
        }

    };
    useEffect(() => {
    })
    return (
        <>
            <Container fixed sx={{ 
                height: '100%', 
                width: '100%',
                minWidth: '100%',
                display: 'flex',
                p: 0
            }}>
                {/* 左侧菜单 */}
                <Sidebar onMenuSelect={setCurrentPage} />
                
                {/* 主内容区域 */}
                <Box sx={{
                    ml: 3,
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    minHeight: '100vh',
                    height: '100%',
                    p: 3
                }}>
                  
                  {currentPage === 'results' ? (
                    <AnalysisResults />
                  ) : (
                    <Box sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        minHeight:'100vh',
                        minWidth: '100%',
                        height: '100%',
                        borderRadius: 3,
                        boxShadow: 3,
                        p: 3,
                        mb: 3,
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        background: 'rgba(255, 255, 255, 0.1)',
                        border: '1px solid var(--border-color)',
                        position: 'relative',
                        overflow: 'hidden',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          right: 0,
                          width: '200px',
                          height: '200px',
                          background: 'radial-gradient(circle, var(--primary-light) 0%, transparent 70%)',
                          opacity: 0.1,
                          zIndex: 0,
                        },
                    }}>
                    <Typography variant="h6" sx={{fontWeight: 'bold'}}>专业分析</Typography>
                    <Box sx={{display: 'flex', justifyContent: 'flex-start', alignItems: 'center',
                        background: 'rgba(255, 255, 255, 0.08)',
                        borderRadius: 2,
                        boxShadow: '0 4px 12px rgba(25, 118, 210, 0.15)',
                        px: 2,
                        py: 1,
                        gap: 2,
                        border: '1px solid rgba(25, 118, 210, 0.2)',
                        position: 'relative',
                        zIndex: 1,
                    }}>

                        {/*<Select value={select1} onChange={e => setSelect1(e.target.value)} sx={{minWidth: 120}}>*/}
                        {/*    <MenuItem value="option1">选项1</MenuItem>*/}
                        {/*    <MenuItem value="option2">选项2</MenuItem>*/}
                        {/*</Select>*/}
                        {/*<Select value={select2} onChange={e => setSelect2(e.target.value)} sx={{minWidth: 120}}>*/}
                        {/*    <MenuItem value="optionA">选项A</MenuItem>*/}
                        {/*    <MenuItem value="optionB">选项B</MenuItem>*/}
                        {/*</Select>*/}
                        <Input placeholder="股票代码" sx={{minWidth: 120}} value={stockCode}
                               onChange={e => setStockCode(e.target.value)}/>
                        <Button variant="contained" sx={{ml: 2}} onClick={getData} disabled={loading}>确定</Button>
                    </Box>
                    <Divider sx={{my: 2}}/>
                    {/* 基本信息区域 */}
                    <Box sx={{
                        minWidth: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        background: 'rgba(255, 255, 255, 0.08)',
                        borderRadius: 2,
                        boxShadow: '0 4px 12px rgba(25, 118, 210, 0.15)',
                        p: 2,
                        mb: 2,
                        border: '1px solid rgba(25, 118, 210, 0.2)',
                        position: 'relative',
                        zIndex: 1,
                    }}>
                        <Typography variant="body2" sx={{minWidth: 120}}>股票名称：{name || '--'}</Typography>
                        <Typography variant="body2" sx={{minWidth: 120}}>股票代码：{stockCode || '--'}</Typography>
                        <Box sx={{minWidth: 120, display: 'flex', alignItems: 'center'}}>
                            <span style={{marginRight: 4}}>风险等级：</span>
                            {action === '低' && <Chip label="低" color="success" size="small"/>}
                            {action === '中' && <Chip label="中" color="error" size="small"/>}
                            {action === '高' && <Chip label="高" color="primary" size="small"/>}
                            {!action && <Chip label="--" size="small"/>}
                        </Box>
                        <Typography variant="body2"
                                    sx={{minWidth: 120}}>当前价格：{currentPrice !== undefined ? currentPrice : '--'}</Typography>
                        <Typography variant="body2"
                                    sx={{minWidth: 120}}>目标价格：{targetPrice !== undefined ? targetPrice : '--'}</Typography>
                    </Box>
                    {/* 下部分内容 */}
                    {loading &&
                        <LinearProgress sx={{position: 'absolute', top: 0, left: 0, width: '100%', zIndex: 1000}}/>}
                    <Divider sx={{my: 2}}/>
                    <Box sx={{flex: 1, display: 'flex', flexDirection: 'column',background: 'rgba(255, 255, 255, 0.1)', borderRadius: 3, boxShadow: '0 8px 24px rgba(59, 130, 246, 0.15)', p: 2, mt: 2,                    minWidth: '100%',
                        border: '1px solid rgba(25, 118, 210, 0.2)',
                        position: 'relative',
                        zIndex: 1,
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          bottom: 0,
                          left: 0,
                          width: '150px',
                          height: '150px',
                          background: 'radial-gradient(circle, var(--primary-light) 0%, transparent 70%)',
                          opacity: 0.05,
                          zIndex: 0,
                        },
                    }}>
                        <Tabs value={tabValue} onChange={(_e, v) => setTabValue(v)} variant="fullWidth" centered sx={{ minHeight: 48,
                            '& .MuiTabs-indicator': {
                                height: 4,
                                borderRadius: 2,
                                background: 'linear-gradient(90deg, #2196f3 0%, #21cbf3 100%)',
                            },
                            mb: 2}}>
                            <Tab label="价格趋势分析"/>
                            <Tab label="技术指标解读"/>
                            <Tab label="新闻情绪分析"/>
                            <Tab label="未来一周预测"/>
                            <Tab label="风险评估"/>
                            <Tab label="操作建议"/>
                            <Tab label="综合结论"/>
                        </Tabs>
                        <Box sx={{p: 2}}>
                            {tabValue === 0 && <ReactMarkdown>{tabData1}</ReactMarkdown>}
                            {tabValue === 1 && <ReactMarkdown>{tabData2}</ReactMarkdown>}
                            {tabValue === 2 && <ReactMarkdown>{tabData3}</ReactMarkdown>}
                            {tabValue === 3 && <ReactMarkdown>{tabData4}</ReactMarkdown>}
                            {tabValue === 4 && <ReactMarkdown>{tabData5}</ReactMarkdown>}
                            {tabValue === 5 && <ReactMarkdown>{tabData6}</ReactMarkdown>}
                            {tabValue === 6 && <ReactMarkdown>{tabData7}</ReactMarkdown>}
                        </Box>
                    </Box>
                </Box>
                )}
                </Box>
            </Container>
        </>
    )
}

export default App
