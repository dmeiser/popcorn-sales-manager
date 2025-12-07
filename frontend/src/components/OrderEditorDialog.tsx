/**
 * OrderEditorDialog - Dialog for creating or editing an order
 * 
 * Features:
 * - Customer information (name, phone, address)
 * - Product selection with quantities
 * - Payment method selection
 * - Order notes
 * - Automatic total calculation
 */

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation } from '@apollo/client/react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Divider,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { CREATE_ORDER, UPDATE_ORDER } from '../lib/graphql';

interface LineItem {
  productId: string;
  productName: string;
  quantity: number;
  pricePerUnit: number;
  subtotal: number;
}

interface Order {
  orderId: string;
  customerName: string;
  customerPhone?: string;
  customerAddress?: {
    street?: string;
    city?: string;
    state?: string;
    zipCode?: string;
  };
  orderDate: string;
  paymentMethod: string;
  lineItems: LineItem[];
  totalAmount: number;
  notes?: string;
}

interface Product {
  productId: string;
  productName: string;
  price: number;
}

interface OrderEditorDialogProps {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
  order: Order | null;
  seasonId: string;
  products: Product[];
}

interface LineItemInput {
  productId: string;
  quantity: number;
}

export const OrderEditorDialog: React.FC<OrderEditorDialogProps> = ({
  open,
  onClose,
  onComplete,
  order,
  seasonId,
  products,
}) => {
  const { profileId } = useParams<{ profileId: string }>();

  // Form state
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [street, setStreet] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<string>('CASH');
  const [lineItems, setLineItems] = useState<LineItemInput[]>([]);
  const [notes, setNotes] = useState('');
  const [orderDate, setOrderDate] = useState('');

  // Initialize form when dialog opens
  useEffect(() => {
    if (open) {
      if (order) {
        // Edit mode
        setCustomerName(order.customerName);
        setCustomerPhone(order.customerPhone || '');
        setStreet(order.customerAddress?.street || '');
        setCity(order.customerAddress?.city || '');
        setState(order.customerAddress?.state || '');
        setZipCode(order.customerAddress?.zipCode || '');
        setPaymentMethod(order.paymentMethod);
        setLineItems(
          order.lineItems.map((item) => ({
            productId: item.productId,
            quantity: item.quantity,
          }))
        );
        setNotes(order.notes || '');
        setOrderDate(order.orderDate.split('T')[0]);
      } else {
        // Create mode
        resetForm();
        setOrderDate(new Date().toISOString().split('T')[0]);
      }
    }
  }, [open, order]);

  const resetForm = () => {
    setCustomerName('');
    setCustomerPhone('');
    setStreet('');
    setCity('');
    setState('');
    setZipCode('');
    setPaymentMethod('CASH');
    setLineItems([]);
    setNotes('');
    setOrderDate('');
  };

  const [createOrder, { loading: creating, error: createError }] = useMutation(CREATE_ORDER, {
    onCompleted: onComplete,
  });

  const [updateOrder, { loading: updating, error: updateError }] = useMutation(UPDATE_ORDER, {
    onCompleted: onComplete,
  });

  const loading = creating || updating;
  const error = createError || updateError;

  const handleAddLineItem = () => {
    if (products.length > 0) {
      setLineItems([...lineItems, { productId: products[0].productId, quantity: 1 }]);
    }
  };

  const handleRemoveLineItem = (index: number) => {
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const handleLineItemChange = (index: number, field: 'productId' | 'quantity', value: string | number) => {
    const newLineItems = [...lineItems];
    if (field === 'productId') {
      newLineItems[index].productId = value as string;
    } else {
      newLineItems[index].quantity = Math.max(1, Number(value));
    }
    setLineItems(newLineItems);
  };

  const calculateTotal = () => {
    return lineItems.reduce((total, item) => {
      const product = products.find((p) => p.productId === item.productId);
      return total + (product ? product.price * item.quantity : 0);
    }, 0);
  };

  const hasAddress = street || city || state || zipCode;
  const isFormValid =
    customerName.trim() &&
    (customerPhone.trim() || hasAddress) &&
    lineItems.length > 0 &&
    orderDate;

  const handleSubmit = async () => {
    if (!isFormValid || !profileId) return;

    const input: any = {
      customerName: customerName.trim(),
      orderDate,
      paymentMethod,
      lineItems: lineItems.map((item) => ({
        productId: item.productId,
        quantity: item.quantity,
      })),
    };

    if (customerPhone.trim()) {
      input.customerPhone = customerPhone.trim();
    }

    if (hasAddress) {
      input.customerAddress = {
        street: street.trim() || undefined,
        city: city.trim() || undefined,
        state: state.trim() || undefined,
        zipCode: zipCode.trim() || undefined,
      };
    }

    if (notes.trim()) {
      input.notes = notes.trim();
    }

    try {
      if (order) {
        // Update existing order
        await updateOrder({
          variables: {
            orderId: order.orderId,
            input,
          },
        });
      } else {
        // Create new order
        await createOrder({
          variables: {
            input: {
              ...input,
              profileId,
              seasonId,
            },
          },
        });
      }
    } catch (err) {
      console.error('Failed to save order:', err);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>{order ? 'Edit Order' : 'New Order'}</DialogTitle>
      <DialogContent>
        <Stack spacing={3} pt={1}>
          {/* Customer Info */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Customer Information
            </Typography>
            <Stack spacing={2}>
              <TextField
                autoFocus
                fullWidth
                label="Customer Name"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                disabled={loading}
                required
              />
              <TextField
                fullWidth
                label="Phone Number"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                disabled={loading}
                helperText="Either phone or address is required"
              />
              <TextField
                fullWidth
                label="Street Address"
                value={street}
                onChange={(e) => setStreet(e.target.value)}
                disabled={loading}
              />
              <Stack direction="row" spacing={2}>
                <TextField
                  fullWidth
                  label="City"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  disabled={loading}
                />
                <TextField
                  label="State"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  disabled={loading}
                  sx={{ width: 100 }}
                />
                <TextField
                  label="ZIP Code"
                  value={zipCode}
                  onChange={(e) => setZipCode(e.target.value)}
                  disabled={loading}
                  sx={{ width: 150 }}
                />
              </Stack>
            </Stack>
          </Box>

          <Divider />

          {/* Order Details */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Order Details
            </Typography>
            <Stack spacing={2}>
              <Stack direction="row" spacing={2}>
                <TextField
                  label="Order Date"
                  type="date"
                  value={orderDate}
                  onChange={(e) => setOrderDate(e.target.value)}
                  disabled={loading}
                  InputLabelProps={{ shrink: true }}
                  required
                  sx={{ flexGrow: 1 }}
                />
                <FormControl sx={{ flexGrow: 1 }}>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={paymentMethod}
                    label="Payment Method"
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    disabled={loading}
                  >
                    <MenuItem value="CASH">Cash</MenuItem>
                    <MenuItem value="CHECK">Check</MenuItem>
                    <MenuItem value="CREDIT_CARD">Credit Card</MenuItem>
                    <MenuItem value="OTHER">Other</MenuItem>
                  </Select>
                </FormControl>
              </Stack>

              {/* Line Items */}
              <Box>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle1">Products</Typography>
                  <Button
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={handleAddLineItem}
                    disabled={loading || products.length === 0}
                  >
                    Add Product
                  </Button>
                </Stack>

                {lineItems.length > 0 ? (
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell align="right">Price</TableCell>
                        <TableCell align="right">Subtotal</TableCell>
                        <TableCell align="right"></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {lineItems.map((item, index) => {
                        const product = products.find((p) => p.productId === item.productId);
                        const subtotal = product ? product.price * item.quantity : 0;
                        return (
                          <TableRow key={index}>
                            <TableCell>
                              <Select
                                fullWidth
                                value={item.productId}
                                onChange={(e) =>
                                  handleLineItemChange(index, 'productId', e.target.value)
                                }
                                disabled={loading}
                                size="small"
                              >
                                {products.map((p) => (
                                  <MenuItem key={p.productId} value={p.productId}>
                                    {p.productName}
                                  </MenuItem>
                                ))}
                              </Select>
                            </TableCell>
                            <TableCell align="right">
                              <TextField
                                type="number"
                                value={item.quantity}
                                onChange={(e) =>
                                  handleLineItemChange(index, 'quantity', e.target.value)
                                }
                                disabled={loading}
                                size="small"
                                sx={{ width: 80 }}
                                inputProps={{ min: 1 }}
                              />
                            </TableCell>
                            <TableCell align="right">
                              ${product?.price.toFixed(2)}
                            </TableCell>
                            <TableCell align="right">
                              <strong>${subtotal.toFixed(2)}</strong>
                            </TableCell>
                            <TableCell align="right">
                              <IconButton
                                size="small"
                                onClick={() => handleRemoveLineItem(index)}
                                disabled={loading}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                      <TableRow>
                        <TableCell colSpan={3} align="right">
                          <strong>Total:</strong>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="h6" color="primary">
                            ${calculateTotal().toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell></TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                ) : (
                  <Alert severity="info">No products added yet. Click "Add Product" to start.</Alert>
                )}
              </Box>

              {/* Notes */}
              <TextField
                fullWidth
                label="Notes (Optional)"
                multiline
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                disabled={loading}
                placeholder="Delivery instructions, special requests, etc."
              />
            </Stack>
          </Box>

          {error && (
            <Alert severity="error">
              Failed to save order: {error.message}
            </Alert>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={!isFormValid || loading}>
          {loading ? 'Saving...' : order ? 'Save Changes' : 'Create Order'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
