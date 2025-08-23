import { Box, Typography, List, ListItem, ListItemText, Divider, Chip, Pagination, TextField, MenuItem, Button, Grid, Paper, CircularProgress, Alert, Select, FormControl, InputLabel } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import { TrendingUp, TrendingDown, TrendingFlat, Search, Clear } from '@mui/icons-material';
import { useState, useMemo } from 'react';
import axios from 'axios';
// 分析结果数据类型定义
interface AnalysisResult {
  id: number;
  stockCode: string;
  stockName: string;
  analysisDate: string;
  currentPrice: number;
  targetPrice: number;
  riskLevel: string;
  recommendation: string;
  trend: string;
}

// 初始为空数组，数据将通过API获取
const mockAnalysisResults: AnalysisResult[] = [
  {
    id: 1,
    stockCode: '600519',
    stockName: '贵州茅台',
    analysisDate: '2024-12-20',
    currentPrice: 1800.50,
    targetPrice: 2000.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 2,
    stockCode: '000858',
    stockName: '五粮液',
    analysisDate: '2024-12-20',
    currentPrice: 150.30,
    targetPrice: 140.00,
    riskLevel: '中',
    recommendation: '持有',
    trend: 'down'
  },
  {
    id: 3,
    stockCode: '601318',
    stockName: '中国平安',
    analysisDate: '2024-12-19',
    currentPrice: 45.20,
    targetPrice: 48.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 4,
    stockCode: '600036',
    stockName: '招商银行',
    analysisDate: '2024-12-19',
    currentPrice: 32.80,
    targetPrice: 32.50,
    riskLevel: '低',
    recommendation: '持有',
    trend: 'flat'
  },
  {
    id: 5,
    stockCode: '000333',
    stockName: '美的集团',
    analysisDate: '2024-12-18',
    currentPrice: 55.60,
    targetPrice: 60.00,
    riskLevel: '中',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 6,
    stockCode: '000001',
    stockName: '平安银行',
    analysisDate: '2024-12-18',
    currentPrice: 12.50,
    targetPrice: 13.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 7,
    stockCode: '000002',
    stockName: '万科A',
    analysisDate: '2024-12-17',
    currentPrice: 8.20,
    targetPrice: 8.50,
    riskLevel: '中',
    recommendation: '持有',
    trend: 'up'
  },
  {
    id: 8,
    stockCode: '000063',
    stockName: '中兴通讯',
    analysisDate: '2024-12-17',
    currentPrice: 28.90,
    targetPrice: 30.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 9,
    stockCode: '000100',
    stockName: 'TCL科技',
    analysisDate: '2024-12-16',
    currentPrice: 4.80,
    targetPrice: 5.00,
    riskLevel: '高',
    recommendation: '持有',
    trend: 'flat'
  },
  {
    id: 10,
    stockCode: '000157',
    stockName: '中联重科',
    analysisDate: '2024-12-16',
    currentPrice: 6.50,
    targetPrice: 6.80,
    riskLevel: '中',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 11,
    stockCode: '000338',
    stockName: '潍柴动力',
    analysisDate: '2024-12-15',
    currentPrice: 15.20,
    targetPrice: 16.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 12,
    stockCode: '000425',
    stockName: '徐工机械',
    analysisDate: '2024-12-15',
    currentPrice: 6.80,
    targetPrice: 7.00,
    riskLevel: '中',
    recommendation: '持有',
    trend: 'up'
  },
  {
    id: 13,
    stockCode: '000538',
    stockName: '云南白药',
    analysisDate: '2024-12-14',
    currentPrice: 55.00,
    targetPrice: 58.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 14,
    stockCode: '000568',
    stockName: '泸州老窖',
    analysisDate: '2024-12-14',
    currentPrice: 200.50,
    targetPrice: 220.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 15,
    stockCode: '000625',
    stockName: '长安汽车',
    analysisDate: '2024-12-13',
    currentPrice: 18.30,
    targetPrice: 19.00,
    riskLevel: '中',
    recommendation: '持有',
    trend: 'up'
  },
  {
    id: 16,
    stockCode: '000651',
    stockName: '格力电器',
    analysisDate: '2024-12-13',
    currentPrice: 38.50,
    targetPrice: 40.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 17,
    stockCode: '000725',
    stockName: '京东方A',
    analysisDate: '2024-12-12',
    currentPrice: 4.20,
    targetPrice: 4.50,
    riskLevel: '高',
    recommendation: '持有',
    trend: 'flat'
  },
  {
    id: 18,
    stockCode: '000768',
    stockName: '中航飞机',
    analysisDate: '2024-12-12',
    currentPrice: 25.80,
    targetPrice: 27.00,
    riskLevel: '中',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 19,
    stockCode: '000858',
    stockName: '五粮液',
    analysisDate: '2024-12-11',
    currentPrice: 152.00,
    targetPrice: 160.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 20,
    stockCode: '000876',
    stockName: '新希望',
    analysisDate: '2024-12-11',
    currentPrice: 12.50,
    targetPrice: 13.00,
    riskLevel: '高',
    recommendation: '持有',
    trend: 'flat'
  },
  {
    id: 21,
    stockCode: '000895',
    stockName: '双汇发展',
    analysisDate: '2024-12-10',
    currentPrice: 25.60,
    targetPrice: 26.50,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 22,
    stockCode: '000938',
    stockName: '紫光股份',
    analysisDate: '2024-12-10',
    currentPrice: 18.90,
    targetPrice: 19.50,
    riskLevel: '中',
    recommendation: '持有',
    trend: 'up'
  },
  {
    id: 23,
    stockCode: '000963',
    stockName: '华东医药',
    analysisDate: '2024-12-09',
    currentPrice: 32.40,
    targetPrice: 34.00,
    riskLevel: '低',
    recommendation: '买入',
    trend: 'up'
  },
  {
    id: 24,
    stockCode: '000983',
    stockName: '西山煤电',
    analysisDate: '2024-12-09',
    currentPrice: 8.70,
    targetPrice: 9.00,
    riskLevel: '中',
    recommendation: '持有',
    trend: 'up'
  },
  {
    id: 25,
    stockCode: '001696',
    stockName: '宗申动力',
    analysisDate: '2024-12-08',
    currentPrice: 6.20,
    targetPrice: 6.50,
    riskLevel: '高',
    recommendation: '持有',
    trend: 'flat'
  }
];

interface AnalysisResultsProps {
  onSelectResult?: (result: any) => void;
}

export default function AnalysisResults({ onSelectResult }: AnalysisResultsProps) {
  const [page, setPage] = useState(1);
  const [searchFilters, setSearchFilters] = useState({
    stockCode: '',
    stockName: '',
    analysisDate: '',
    riskLevel: ''
  });
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const itemsPerPage = 10;

  const filteredResults = useMemo(() => {
    return analysisResults.filter(result => {
      return (
        (!searchFilters.stockCode || result.stockCode.includes(searchFilters.stockCode)) &&
        (!searchFilters.stockName || result.stockName.includes(searchFilters.stockName)) &&
        (!searchFilters.analysisDate || result.analysisDate === searchFilters.analysisDate) &&
        (!searchFilters.riskLevel || result.riskLevel === searchFilters.riskLevel)
      );
    });
  }, [analysisResults, searchFilters]);

  const paginatedResults = useMemo(() => {
    const startIndex = (page - 1) * itemsPerPage;
    return filteredResults.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredResults, page]);

  const totalPages = Math.ceil(filteredResults.length / itemsPerPage);
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp color="success" />;
      case 'down':
        return <TrendingDown color="error" />;
      case 'flat':
        return <TrendingFlat color="action" />;
      default:
        return <TrendingFlat color="action" />;
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case '低':
        return 'success';
      case '中':
        return 'warning';
      case '高':
        return 'error';
      default:
        return 'default';
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case '买入':
        return 'success';
      case '持有':
        return 'warning';
      case '卖出':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleSearchChange = (field: string, value: string) => {
    setSearchFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setPage(1); // 重置到第一页
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // 构建查询参数
      const params = new URLSearchParams();
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });
      
      // 调用API获取分析结果
      const response = await axios.get(`/api/analysis/results?${params.toString()}`);
      setAnalysisResults(response.data.results || []);
      setPage(1); // 重置到第一页
    } catch (err) {
      console.error('获取分析结果失败:', err);
      setError('获取分析结果失败，请稍后重试');
      setAnalysisResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setSearchFilters({
      stockCode: '',
      stockName: '',
      analysisDate: '',
      riskLevel: ''
    });
    setPage(1);
    setAnalysisResults([]);
    setError(null);
  };

  // 获取唯一的分析日期用于下拉选项
  const uniqueDates = useMemo(() => {
    return Array.from(new Set(analysisResults.map(item => item.analysisDate))).sort().reverse();
  }, [analysisResults]);

  return (
    <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', minHeight: '100%' }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3, color: 'rgba(0, 0, 0, 0.87)' }}>
        分析结果列表
      </Typography>

      {/* 搜索条件区域 */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'rgba(255, 255, 255, 0.08)' }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'medium', mb: 2, color: 'rgba(0, 0, 0, 0.87)' }}>
          搜索条件
        </Typography>
        <Box component="form" onSubmit={handleSearchSubmit}>
          <Grid container spacing={2} alignItems="center">
          <Grid size={{xs:2}}>
            <TextField
              fullWidth
              label="股票代码"
              value={searchFilters.stockCode}
              onChange={(e) => handleSearchChange('stockCode', e.target.value)}
              placeholder="输入股票代码"
              size="small"
            />
          </Grid>
          <Grid size={{xs:2}}>
            <TextField
              fullWidth
              label="股票名称"
              value={searchFilters.stockName}
              onChange={(e) => handleSearchChange('stockName', e.target.value)}
              placeholder="输入股票名称"
              size="small"
            />
          </Grid>
          <Grid size={{xs:4}}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DatePicker
                label="分析日期"
                value={searchFilters.analysisDate ? dayjs(searchFilters.analysisDate) : null}
                onChange={(date) => handleSearchChange('analysisDate', date ? date.format('YYYY-MM-DD') : '')}
                format="YYYY-MM-DD"
                slotProps={{
                  textField: {
                    fullWidth: true,
                    size: 'small',
                    placeholder: '选择日期'
                  }
                }}
              />
            </LocalizationProvider>
          </Grid>
          <Grid size={{xs:2}}>
            <FormControl fullWidth size="small">
              <InputLabel>风险等级</InputLabel>
              <Select
                value={searchFilters.riskLevel}
                label="风险等级"
                onChange={(e) => handleSearchChange('riskLevel', e.target.value)}
              >
                <MenuItem value="">
                  <em>全部等级</em>
                </MenuItem>
                <MenuItem value="低">低风险</MenuItem>
                <MenuItem value="中">中风险</MenuItem>
                <MenuItem value="高">高风险</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          </Grid>
          
          {/* 按钮区域 - 单独一行 */}
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={{xs:12}} sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Button
                type="button"
                variant="outlined"
                startIcon={<Clear />}
                onClick={handleClearFilters}
                size="small"
              >
                清空条件
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={<Search />}
                size="small"
                disabled={loading || Object.values(searchFilters).every(val => !val)}
              >
                {loading ? <CircularProgress size={16} sx={{ mr: 1 }} /> : <Search />}
                搜索
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Paper>
      
      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {/* 加载状态 */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}
      
      <Typography variant="subtitle1" sx={{ mb: 2, color: 'rgba(0, 0, 0, 0.6)' }}>
        共找到 {filteredResults.length} 条分析结果
      </Typography>

      <List sx={{ width: '100%', bgcolor: 'rgba(255, 255, 255, 0.1)', flex: 1 }}>
        {paginatedResults.map((result, index) => (
          <Box key={result.id}>
            <ListItem 
              alignItems="flex-start"
              sx={{ 
                '&:hover': { 
                  bgcolor: 'action.hover',
                  cursor: 'pointer' 
                },
                borderRadius: 2,
                mb: 1
              }}
              onClick={() => onSelectResult?.(result)}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="h6" component="span" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                      {result.stockName}
                    </Typography>
                    <Typography variant="body2" component="span" sx={{ color: 'rgba(0, 0, 0, 0.6)' }}>
                      ({result.stockCode})
                    </Typography>
                    {getTrendIcon(result.trend)}
                  </Box>
                }
                secondary={
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                      <Chip 
                        label={`当前: ¥${result.currentPrice}`} 
                        size="small" 
                        variant="outlined" 
                      />
                      <Chip 
                        label={`目标: ¥${result.targetPrice}`} 
                        size="small" 
                        color="primary" 
                      />
                      <Chip 
                        label={result.riskLevel} 
                        size="small" 
                        color={getRiskColor(result.riskLevel) as any}
                      />
                      <Chip 
                        label={result.recommendation} 
                        size="small" 
                        color={getRecommendationColor(result.recommendation) as any}
                        variant="filled"
                      />
                    </Box>
                    <Typography variant="caption" sx={{ color: 'rgba(0, 0, 0, 0.6)' }}>
                      分析日期: {result.analysisDate}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
            {index < paginatedResults.length - 1 && <Divider variant="inset" component="li" />}
          </Box>
        ))}
      </List>
      
      {/* 分页控件 */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={(_event, value) => setPage(value)}
          color="primary"
          showFirstButton
          showLastButton
          sx={{ 
            '& .MuiPaginationItem-root': {
              fontSize: '0.875rem',
            }
          }}
        />
      </Box>
      
      {filteredResults.length === 0 && (
        <Box sx={{ 
          textAlign: 'center', 
          py: 8, 
          color: 'text.secondary' 
        }}>
          <Typography variant="h6" gutterBottom>
            暂无分析结果
          </Typography>
          <Typography variant="body2">
            请先进行股票分析以生成分析结果
          </Typography>
        </Box>
      )}
    </Box>
  );
}