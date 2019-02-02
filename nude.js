var Canvas = require('canvas'),
  fs = require('fs'),
  Image = Canvas.Image;
var t=0;
var count=0
var classifySkin = function(r, g, b) {
	//console.log(r);
    var rgbClassifier = r > 95 && g > 40 && g < 100 && b > 20 && (Math.max(r, g, b) - Math.min(r, g, b)) > 15 && Math.abs(r - g) > 15 && r > g && r > b,
      nurgb = toNormalizedRgb(r, g, b),
      nr = nurgb[0],
      ng = nurgb[1];
      //if(ng==0) {console.log("nr="+nr+"ng="+ng+"r="+nr/ng); console.log((nr/ng)>1.185);return;}
      var nb = nurgb[2],
      normRgbClassifier = (nr / ng) > 1.185 && (r * b / Math.pow(r + g + b, 2)) > 0.107 && (r * g / Math.pow(r + g + b, 2)) > 0.112,
      hsv = toHsvTest(r, g, b),
      //console.log("y");
      //console.log("y");
      h = hsv[0];
      //if(r==19&&isNaN(h)){ console.log(typeof h); console.log(h>0);t=1;}
      var s = hsv[1],
      hsvClassifier = h > 0 && h < 35 && s > 0.23 && s < 0.68;
      //if(b==0) console.log("c="+count+"r="+rgbClassifier || normRgbClassifier || hsvClassifier);
      return rgbClassifier || normRgbClassifier || hsvClassifier;
  },
  toHsvTest = function(r, g, b) {
	  //if(r==g && g==b) if(t==0){console.log(r,g,b);t=1;}
	  var h = 0,
	    mx = Math.max(r, g, b),
	    mn = Math.min(r, g, b),
	    dif = mx - mn;
	  if(mx == r)
		  h = (g - b) / dif;
	  else if(mx == g)
		  h = 2 + (g - r) / dif;
	  else
		  h = 4 + (r - g) / dif;
	  h *= 60;
	  if(h < 0)
		  h += 360;
	  return [h, 1 - 3 * (Math.min(r, g, b) / (r + g + b)), 1 / 3 * (r + g + b)];
  },
  toNormalizedRgb = function(r, g, b) {
	  var sum = r + g + b;
	  //if(sum==0) console.log(r/sum);
	  return [r / sum, g / sum, b / sum];
  };

module.exports = {
  scan: function(src, callback) {
    fs.readFile(src, function(err, data) {
      if(err)
        throw err;
      var canvas = new Canvas(1, 1),
        ctx = canvas.getContext('2d'),
        img = new Image,
        skinRegions = [],
			  skinMap = [],
			  detectedRegions = [],
			  mergeRegions = [],
			  detRegions = [],
			  lastFrom = -1,
			  lastTo = -1,
        totalSkin = 0,
			  addMerge = function(from, to) {
				  //if(t==0){console.log("dd");t=1;}
				  lastFrom = from;
				  lastTo = to;
				  var len = mergeRegions.length,
				    fromIndex = -1,
				    toIndex = -1,
				    region,
				    rlen;
				    //console.log(len+"f");
				    //console.log(mergeRegions);
				  while(len--) {
					  //console.log(len+"f");
					  region = mergeRegions[len];
					  //console.log(region);
					  rlen = region.length;
					  while(rlen--) {
						  if(region[rlen] == from)
							  fromIndex = len;
						  if(region[rlen] == to)
							  toIndex = len;
					  }
				  }
				  if(fromIndex != -1 && toIndex != -1 && fromIndex == toIndex)
					  return;
				  if(fromIndex == -1 && toIndex == -1)
					  return mergeRegions.push([from, to]);
				  if(fromIndex != -1 && toIndex == -1)
					  return mergeRegions[fromIndex].push(to);
				  if(fromIndex == -1 && toIndex != -1)
					  return mergeRegions[toIndex].push(from);
				  if(fromIndex != -1 && toIndex != -1 && fromIndex != toIndex) {
					  mergeRegions[fromIndex] = mergeRegions[fromIndex].concat(mergeRegions[toIndex]);
					  mergeRegions = [].concat(mergeRegions.slice(0, toIndex), mergeRegions.slice(toIndex + 1));
				  }
			  },
			  totalPixels,
			  imageData,
			  length;
      img.src = data;
		  canvas.width = img.width;
		  canvas.height = img.height;
		  totalPixels = canvas.width * canvas.height;
		  ctx.drawImage(img, 0, 0);
      imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      //console.log("y"+imageData[0]+"y"+imageData[1]+"y"+imageData[2]+"y"+imageData[4]+"y"+imageData[5]+"y"+imageData[6])
			length = imageData.length;
			console.log(canvas.width+' '+canvas.height+' '+length)
			for(var i = 0, u = 0; i < length; i += 4, u++) {
				//if(i>2000) return;
				var r = imageData[i],
				  g = imageData[i + 1],
				  b = imageData[i + 2],
				  x = u % canvas.width;
				  //if(i==749996) console.log("gg"+imageData[i]+"d"+imageData[i+1]+"d"+imageData[i+2]);
				  y = Math.floor(u / canvas.width);
				  //console.log("u"+u+"w"+canvas.width+"x"+x+"y"+y);
				  //console.log(r+"s"+g+"g"+b)
				if(classifySkin(r, g, b)) {
					count+=1;
					//console.log(count);
					skinMap.push({id: u, skin: true, region: 0, x: x, y: y, checked: false});
					var region = -1,
					  checkIndexes = [u - 1, u - canvas.width - 1, u - canvas.width, u - canvas.width + 1],
					  checker = false;
					  
					for(var o = 0, index; o < 4; o++) {
						index = checkIndexes[o];
						//console.log(skinMap[index].region+"c"+region+"c"+lastFrom+"c"+lastTo);
						if(skinMap[index] && skinMap[index].skin) {
							//console.log("work");
							if(skinMap[index].region != region && region != -1 && lastFrom != region && lastTo != skinMap[index].region)
								{addMerge(region, skinMap[index].region);}
									//console.log("again");}
							region = skinMap[index].region;
							checker = true;
						}
					}
					//console.log(mergeRegions);
					//console.log("c"+count);
					//if(count==100) {console.log(mergeRegions.length);return;}
					if(!checker) {
						//if(t==0){console.log(detectedRegions.length);t=0;}
						skinMap[u].region = detectedRegions.length;
						//console.log(detectedRegions.length);return;
						detectedRegions.push([skinMap[u]]);
						//console.log("here");
						//if(t==0){console.log(detectedRegions);t=1;}
						//continue;
					}
					else{
						//console.log("there");
						if(region > -1) {
							//if(!detectedRegions[region]) console.log("yoyo");
							//else console.log("koko");
							if(!detectedRegions[region])
								detectedRegions[region] = [];
							skinMap[u].region = region;
							detectedRegions[region].push(skinMap[u]);
						}}
				}
				else skinMap.push({ id: u, skin: false, region: 0, x: x, y: y, checked: false });
				//if(i==2000) console.log(skinMap);
					//if(t==0){console.log("sum="+skinMap[1]);t=1;}}
			}
			//console.log("done");
			//console.log(skinMap);
			//console.log(mergeRegions);
			//console.log(mergeRegions.length);
			//console.log(mergeRegions);
			//console.log(detectedRegions.length);
			length = mergeRegions.length;
			//console.log(skinMap);
			//console.log(length+"l");
			//return;
			var test=0;
			while(length--) {
				region = mergeRegions[length];
				var rlen = region.length;
				//console.log("y");
				//console.log(detRegions);
				if(!detRegions[length])
					detRegions[length] = [];
				//console.log(detRegions);
				//console.log("y");
				while(rlen--) {
					test+=1;
					index = region[rlen];
					//console.log(detRegions);
					//console.log(detectedRegions[index]);
					detRegions[length] = detRegions[length].concat(detectedRegions[index]);
					//if(test==100) {console.log(detRegions);return;}
					detectedRegions[index] = [];
				}
			}
			//console.log(detRegions);
			//console.log(detectedRegions);
			//console.log(detRegions.length);
			//console.log(detectedRegions.length);
			//return;
			length = detectedRegions.length;
			while(length--)
				if(detectedRegions[length].length > 0)
					detRegions.push(detectedRegions[length]);
			//console.log(detRegions);
			//return;
			length = detRegions.length;
			for(var i = 0; i < length; i++)
				if(detRegions[i].length > 30)
					skinRegions.push(detRegions[i]);
			length = skinRegions.length;
			
			if(length < 3)
				return callback && callback(false);
			//console.log("0");
			(function() {
				var sorted = false, temp;
				while(!sorted) {
					sorted = true;
					for(var i = 0; i < length-1; i++)
						if(skinRegions[i].length < skinRegions[i + 1].length) {
							sorted = false;
							temp = skinRegions[i];
							skinRegions[i] = skinRegions[i + 1];
							skinRegions[i + 1] = temp;
						}
				}
			})();
			//console.log("0");
			//console.log(skinRegions[0].length);
			//if(t==0){console.log(detectedRegions);t=1;}
			while(length--)
				{console.log(skinRegions[length].length);totalSkin += skinRegions[length].length;}
			console.log('k'+totalSkin+'k'+totalPixels);
			if((totalSkin / totalPixels) * 100 < 15)
				return callback && callback(false);
			if((skinRegions[0].length / totalSkin) * 100 < 35 && (skinRegions[1].length / totalSkin) * 100 < 30 && (skinRegions[2].length / totalSkin) * 100 < 30)
				return callback && callback(false);
			if((skinRegions[0].length / totalSkin) * 100 < 45)
				return callback && callback(false);
			if(skinRegions.length > 60)
				return callback && callback(false);
			return callback && callback(true);
		});
  }
};
